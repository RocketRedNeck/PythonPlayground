# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 20:59:54 2016

@author: mtkessel
"""

import numpy as np
import subprocess as sp
import picamera
import picamera.array
import threading
import time
import io
from PIL import Image, ImageDraw, ImageFont

CAMW, CAMH = 640, 320
NBYTES = CAMW * CAMH * 3
npa = np.zeros((CAMH, CAMW, 3), dtype=np.uint8)
new_pic = False

# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []

class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.start()

    def run(self):
        # This method runs in a separate thread
        global done, npa, new_pic, CAMH, CAMW, NBYTES
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    if self.stream.tell() >= NBYTES:
                      self.stream.seek(0)
                      # python2 doesn't have the getbuffer() method
                      #bnp = np.fromstring(self.stream.read(NBYTES), 
                      #              dtype=np.uint8).reshape(CAMH, CAMW, 3)
                      # if using python3 this should be faster              
                      bnp = np.array(self.stream.getbuffer(), 
                                    dtype=np.uint8).reshape(CAMH, CAMW, 3)
                      npa[:,:,0:3] = bnp
                      new_pic = True
                except Exception as e:
                  print(e)
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the pool
                    with lock:
                        pool.append(self)

def streams():
    while not done:
        with lock:
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            yield processor.stream
            processor.event.set()
        else:
            # When the pool is starved, wait a while for it to refill
            time.sleep(0.1)


def start_capture(): # has to be in yet another thread as blocking
  global CAMW, CAMH, pool
  with picamera.PiCamera() as camera:
    pool = [ImageProcessor() for i in range(5)]
    camera.resolution = (CAMW, CAMH)
    camera.framerate = 10
    #camera.start_preview()
    time.sleep(2)
    camera.capture_sequence(streams(), format='rgb', use_video_port=True)

t = threading.Thread(target=start_capture)
t.start()


while not new_pic:
    time.sleep(0.1)

command = ['ffmpeg',
        '-y', # (optional) overwrite output file if it exists
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        '-s', '{}x{}'.format(CAMW, CAMH), # size of one frame
        '-pix_fmt', 'rgb24',
        '-r', '10', # frames per second
        '-i', '-', # The imput comes from a pipe
        '-an', # Tells FFMPEG not to expect any audio
        '-vcodec', 'h264',
        'my_output_videofile2.h264' ]

pipe = sp.Popen(command, stdin=sp.PIPE, bufsize=-1)

imgfont = ImageFont.truetype('fonts/FreeSans.ttf', 24)
img = Image.new("L", (CAMW, CAMH), 0)
draw = ImageDraw.Draw(img)
txt = ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog']
txt_i = 0
tm = 0.0

try: # ctl-c to stop the program
  while True:
    pipe.stdin.write(npa.tostring())
    if  new_pic:
      if time.time() > tm: # only change text now and then
        if txt_i == 0:
          img.paste(0) # set to zero
        draw.text((10, 10 + 20 * txt_i), txt[txt_i], font=imgfont, fill=255)
        txt_i = (txt_i + 1) % len(txt)
        t_xy = np.where(np.array(img) > 0)
        tm = time.time() + 2.0
      npa[t_xy[0], t_xy[1]] = [255, 0, 0] # red letters
      new_pic = False
except:
  pipe.terminate()
  # Shut down the processors in an orderly fashion
  while pool:
    done = True
    with lock:
      processor = pool.pop()
    processor.terminated = True
    processor.join()