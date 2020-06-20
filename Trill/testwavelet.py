from scipy import signal
from wavelets import WaveletAnalysis
import numpy as np
import matplotlib.pyplot as plt

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
sig = sig0 + sig1 + sig2 + sig3 + sig1a

plt.subplot(4,1,1)
plt.plot(t,sig)
plt.xlim(t[0],t[-1])

N = 1024 #Number of point in the fft
f, ts, Sxx = signal.spectrogram(sig, fs,window = signal.hanning(N),nfft=N, noverlap=512)
plt.subplot(4,1,2)
plt.pcolormesh(ts, f,10*np.log10(Sxx)) # dB spectrogram
plt.ylim(0,fhz*2)
#plt.pcolormesh(t, f,Sxx) # Lineal spectrogram
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time')

w = 1024
widths = np.arange(1, w)
cwtmatr = signal.cwt(sig, signal.ricker, widths)
plt.subplot(4,1,3)
plt.imshow(cwtmatr, extent=[t[0], t[-1], widths[0], widths[-1]], cmap='seismic', aspect='auto',  #cmap='PRGn'
           vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())
plt.ylim(w-w/4,w)
# given a signal x(t)
x = sig #np.random.randn(1000)

# and a sample spacing
dt = 1/fs #0.1

wa = WaveletAnalysis(x, dt=dt)

# wavelet power spectrum
power = wa.wavelet_power

# scales 
scales = wa.scales

# associated time vector
t = wa.time

# reconstruction of the original data
rx = wa.reconstruction()


ax = plt.subplot(4,1,4)
T, S = np.meshgrid(t, scales)
ax.contourf(T, S, power, 100)
ax.set_yscale('log')

plt.show()
