# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 20:46:25 2017

@author: mtkes
"""

# import the necessary packages
from __future__ import print_function
import cv2

from imutils.video import WebcamVideoStream
from imutils.video import FPS

import time
 
# grab a pointer to the video stream and initialize the FPS counter
print("[INFO] sampling frames from webcam...")
stream = cv2.VideoCapture(1)
w = 320
h = 240
e = -50.0
t = 10.0

stream.set(cv2.CAP_PROP_FRAME_WIDTH,w)
stream.set(cv2.CAP_PROP_FRAME_HEIGHT,h)
stream.set(cv2.CAP_PROP_EXPOSURE, e)

fps = FPS().start()
 
# loop over some frames for the specified time
startTime = time.clock()
frameCount = 0

#while fps._numFrames < args["num_frames"]:
while (time.clock() - startTime < t):
    # grab the frame from the stream and resize it to have a maximum
    # width of 400 pixels
    (grabbed, frame) = stream.read()
    #frame = imutils.resize(frame, width=400)
 
    # check to see if the frame should be displayed to our screen
    if (grabbed == True):
        cv2.putText(frame,str(frameCount),(0,240),cv2.FONT_HERSHEY_PLAIN,2,(0,0,255))
        frameCount = frameCount + 1
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
 
    # update the FPS counter
    fps.update()
 
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
# do a bit of cleanup
stream.release()
cv2.destroyAllWindows()

# created a *threaded* video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from webcam...")
vs = WebcamVideoStream(src=1).start()

vs.stream.set(cv2.CAP_PROP_FRAME_WIDTH,w)
vs.stream.set(cv2.CAP_PROP_FRAME_HEIGHT,h)
vs.stream.set(cv2.CAP_PROP_EXPOSURE, e)

fps = FPS().start()
 
# loop over some frames...this time using the threaded stream
startTime = time.clock()
frameCount = 0

#while fps._numFrames < args["num_frames"]:
while (time.clock() - startTime < t):
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    frame = vs.read()
    #frame = imutils.resize(frame, width=400)
 
    # check to see if the frame should be displayed to our screen
    if (grabbed == True):
        cv2.putText(frame,str(frameCount),(0,240),cv2.FONT_HERSHEY_PLAIN,2,(0,0,255))
        frameCount = frameCount + 1
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

    # update the FPS counter
    fps.update()
 
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()