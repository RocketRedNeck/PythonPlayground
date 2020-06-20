from scipy.io import wavfile # scipy library to read wav files
import numpy as np

import pydub # library with mp3 reader, install via pip (does not exist in conda universe)
# NOTE: Must install ffmpeg to use pydub (https://ffmpeg.zeranoe.com/builds/)
# Install ffmpeg to directory like C:\ffmpeg and add C:\ffmpeg\bin to PATH

import random
import matplotlib.pyplot as plt
import os


class mp3:
    def read(self,f, normalized=False):
        """MP3 to numpy array"""
        a = pydub.AudioSegment.from_mp3(f)
        y = np.array(a.get_array_of_samples())
        if a.channels == 2:
            y = y.reshape((-1, 2))
        if normalized:
            return a.frame_rate, np.float32(y) / 2**15
        else:
            return a.frame_rate, y

    def write(self,f, sr, x, normalized=False):
        """numpy array to MP3"""
        channels = 2 if (x.ndim == 2 and x.shape[1] == 2) else 1
        if normalized:  # normalized array - each item should be a float in [-1, 1)
            y = np.int16(x * 2 ** 15)
        else:
            y = np.int16(x)
        song = pydub.AudioSegment(y.tobytes(), frame_rate=sr, sample_width=2, channels=channels)
        song.export(f, format="mp3", bitrate="320k")


rootdir = './Voices of Western Backyard Birds/'
d = os.listdir(rootdir)

AudioName = []
for f in d[1:]:
    n = os.path.abspath(os.path.join(rootdir,f))
    if '.mp3' in n or '.wav' in n:
        AudioName.append(n.replace('\\','/'))

mp3 = mp3()
plt.figure()
i = 1
for nm in AudioName:
    if "mp3" in nm:
        fs, Audiodata0 = mp3.read(nm)
    else:
        fs, Audiodata0 = wavfile.read(nm)

    n = len(Audiodata0)
    tmax = n/fs
    t = np.linspace(0, tmax, n, endpoint=False)

    plt.subplot(len(AudioName),1,i)
    i += 1
    plt.plot(t,Audiodata0)

plt.show()
