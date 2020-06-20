from scipy.io import wavfile # scipy library to read wav files
import numpy as np

import pydub # library with mp3 reader, install via pip (does not exist in conda universe)
# NOTE: Must install ffmpeg to use pydub (https://ffmpeg.zeranoe.com/builds/)
# Install ffmpeg to directory like C:\ffmpeg and add C:\ffmpeg\bin to PATH

import random

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

import os

AudioName = "./Voices of Western Backyard Birds/16 White-crowned Sparrow Song 1.mp3" # Audio File
AudioName = "./Voices of Western Backyard Birds/21 Cassin's Finch Song.mp3"
#AudioName = "./Voices of Western Backyard Birds/19 Red-winged Blackbird Song.mp3"
AudioName = os.path.abspath(AudioName)
AudioName.replace('\\','/')      # Needed to fix problem with pydub path handling

if "mp3" in AudioName:
    mp3 = mp3()
    fs, Audiodata0 = mp3.read(AudioName)
else:
    fs, Audiodata0 = wavfile.read(AudioName)

n = len(Audiodata0)
tmax = n/fs
t = np.linspace(0, tmax, n, endpoint=False)
#index = np.where((t > 1.3) & (t < 2.3))
index = np.where((t > 1.5) & (t < 3.5))
t = t[index]
Audiodata0 = Audiodata0[index]
n = len(Audiodata0)

# generate random floating point values
from numpy.random import seed
from numpy.random import rand

# seed random number generator
seed(1)
# generate random numbers between 0-1
nnoise = 5
noise = rand(len(Audiodata0)) * (2/nnoise)*float(max(Audiodata0))

for i in range(0,nnoise+1):
    
    Audiodata = Audiodata0 + noise*i

    # Plot the audio signal in time
    import matplotlib.pyplot as plt

    r = 4
    c = 1


    print('********************************')
    print(n, fs, tmax, len(t))

    plt.figure()
    plt.subplot(r,c,1)
    plt.plot(t-t[0],Audiodata)
    plt.xlim(0,t[-1] - t[0])
    plt.title('Audio signal in time')

    # spectrum (TODO: add CWT and DWT for different spectra)
    from scipy.fftpack import fft # fourier transform
    AudioFreq = fft(Audiodata)
    AudioFreq = AudioFreq[0:int(np.ceil((n+1)/2.0))] #Half of the spectrum
    MagFreq = np.abs(AudioFreq) # Magnitude
    MagFreq = MagFreq / float(n)



    # power spectrum
    MagFreq = MagFreq**2
    if n % 2 > 0: # ffte odd 
        MagFreq[1:len(MagFreq)] = MagFreq[1:len(MagFreq)] * 2
    else:# fft even
        MagFreq[1:len(MagFreq) -1] = MagFreq[1:len(MagFreq) - 1] * 2 

    plt.subplot(r,c,2)
    freqAxis = np.arange(0,int(np.ceil((n+1)/2.0)), 1.0) * (fs / n)
    plt.plot(freqAxis/1000.0, 10*np.log10(MagFreq)) #Power spectrum
    plt.xlabel('Frequency (kHz)') 
    plt.ylabel('Power spectrum (dB)')


    #Spectrogram
    from scipy import signal

    N = 256 #Number of point in the fft
    f, ts, Sxx = signal.spectrogram(Audiodata, fs,window = signal.blackman(N),nfft=N,noverlap=128)
    plt.subplot(r,c,3)
    plt.pcolormesh(ts, f,10*np.log10(Sxx)) # dB spectrogram
    #plt.yscale('log')
    #plt.ylim(100,7000)
    #plt.pcolormesh(t, f,Sxx) # Lineal spectrogram
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (seg)')

    # scipy cwt is confusing
    # Consider custom library: https://github.com/aaren/wavelets
    # From https://stackoverflow.com/questions/23730383/where-can-i-see-the-list-of-built-in-wavelet-functions-that-i-can-pass-to-scipy
    # w = 1024
    # widths = np.arange(w/8, w)
    # cwtmatr = signal.cwt(Audiodata, signal.ricker, widths)
    # plt.subplot(r,c,4)
    # print(cwtmatr.size)
    # plt.imshow(cwtmatr, extent=[0, t[-1] - t[0], widths[0], widths[-1]], cmap='seismic', aspect='auto',
    #         vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())

    from wavelets import WaveletAnalysis
    from wavelets import Ricker
    wa = WaveletAnalysis(Audiodata, dt=1/fs) #, wavelet=Ricker())

    # wavelet power spectrum
    power = wa.wavelet_power

    # scales 
    scales = wa.scales

    # associated time vector
    t = wa.time
    ax = plt.subplot(r,c,4)
    T, S = np.meshgrid(t, scales)
    ax.contourf(T, S, power, 100)
    ax.set_yscale('log')


plt.show()
