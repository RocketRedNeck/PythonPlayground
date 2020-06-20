from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

r = 3
c = 1

fs = 2000
tmax = 1.0
t = np.linspace(0, tmax, fs, endpoint=False)
fhz = 50
f0 = 2*np.pi*fhz
print(f'f0 = {f0}')
sig0 = np.cos(f0*t)
sig1 = np.cos(0.5*f0*t)
sig2 = np.cos(0.1*f0*t)
sig1a = np.cos(0.7*f0*t)
sig3 = np.cos(0.05*f0*t)
sig = sig0 + sig1 + sig2 + sig3 #+ sig1a
plt.subplot(r,c,1)
plt.plot(t,sig)
plt.xlim(t[0],t[-1])

N = 1024 #Number of point in the fft
f, ts, Sxx = signal.spectrogram(sig, fs,window = signal.blackman(N),nfft=N, noverlap=N-128)
plt.subplot(r,c,2)
plt.pcolormesh(ts, f,10*np.log10(Sxx)) # dB spectrogram
plt.ylim(0,fhz*2)
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