from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

t = np.linspace(0, 2, 200, endpoint=False)
sig  = np.cos(2 * np.pi * 7 * t) + signal.gausspulse(t - 0.5, fc=3)


widths = np.arange(1, 31)
cwtmatr = signal.cwt(sig, signal.ricker, widths)
plt.subplot(2,1,1)
plt.plot(t,sig)
plt.subplot(2,1,2)
plt.imshow(cwtmatr, extent=[0, 2, 1, 31], cmap='PRGn', aspect='auto',
           vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())
plt.show()