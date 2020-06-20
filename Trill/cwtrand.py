from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

from numpy.random import seed
from numpy.random import rand

r = 3
c = 1

fs = 44100
tmax = 1.0
t = np.linspace(0, tmax, fs, endpoint=False)
seed(1)
for i in range(1,4):
    noise = rand(len(t))
    sig = noise

    plt.figure()
    plt.subplot(r,c,1)
    plt.plot(t,sig)
    plt.xlim(t[0],t[-1])

    N = 1024 #Number of point in the fft
    f, ts, Sxx = signal.spectrogram(sig, fs,window = signal.blackman(N),nfft=N)
    plt.subplot(r,c,2)
    plt.pcolormesh(ts, f,10*np.log10(Sxx)) # dB spectrogram
    #plt.pcolormesh(t, f,Sxx) # Lineal spectrogram
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time')


    w = 128
    widths = np.arange(1, w)
    cwtmatr = signal.cwt(sig, signal.ricker, widths)
    plt.subplot(r,c,3)
    plt.imshow(cwtmatr, extent=[t[0], t[-1], widths[0], widths[-1]], cmap='seismic', aspect='auto',  #cmap='PRGn'
            vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())

plt.show()