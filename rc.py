
# Standard imports
from matplotlib import pyplot as pl
import numpy as np
from scipy import integrate

# 3rd party imports

# local imports

tmax = 1
tstep = 0.001

V0 = 35

R = 0.1

N = 100
C0 = 10e-3

CX = np.array(N*[C0])

charge_modes = {#'Series'   : True,
                'Parallel' : False
               }


t = np.arange(0, tmax, tstep)

for mode in charge_modes:
    
    series = charge_modes[mode]

    if series:
        ooc = np.ones(CX.shape) / CX
        C = 1 / np.sum(ooc)
    else:
        C = np.sum(CX)

    print(f'Mode: {mode} C = {C}')

    tau = R * C

    tot = t/tau

    VC = V0*(1.0 - np.e**-tot)
    Q = C*VC
    IC = V0/R*(np.e**-tot)

    fig1 = pl.figure()
    pl.subplot(3,1,1)
    pl.title(f"Capacitor Charge Up ({mode})")
    pl.plot(t,VC)
    pl.ylabel("Volts")
    pl.subplot(3,1,2)
    pl.plot(t,Q)
    pl.ylabel("Coulomb/Volt")
    pl.subplot(3,1,3)
    pl.plot(t,IC)
    pl.ylabel("Amp")
    pl.xlabel("Time (s)")

    P = VC * IC
    E = integrate.cumtrapz(P, t)

    fig2, ax2 = pl.subplots()

    color = 'tab:red'
    ax2.set_title(f"Capcitor Charge Power and Energy ({mode})")
    ax2.set_xlabel('time (s)')
    ax2.set_ylabel('Watt', color=color)
    ax2.plot(t, P, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    ax3 = ax2.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax3.set_ylabel('Joule', color=color)  # we already handled the x-label with ax1
    ax3.plot(t[0:-1], E, color=color)
    ax3.tick_params(axis='y', labelcolor=color)

    fig2.tight_layout()  # otherwise the right y-label is slightly clipped


pl.show()



