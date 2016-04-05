# Perform I-V sweep (static), then perform MPPT (P&O) and plot power over time
# dynamically. Also plots power over time of another panel using DMMs.
# Used in combination with a C++ GUI.
# Creates/overwrites: flag.dat

# Author: Andrew Morrison
# Last edit by Felix Hsiao on Jan. 20, 2016
# Based on code from Shibin Qin and Chris Barth

import time
import collections
from pilawa_instruments import prologix_serial, prologix_6060b, prologix_34461a
import matplotlib as mpl
import matplotlib.pyplot as plt

## Constants ##
ELOAD_ADDR = 4
VDMM_ADDR = 2
IDMM_ADDR = 12
V_OC = 13.5  # Volts; I-V sweep end-voltage (inclusive) and max voltage that
             # can be manually set during MPPT
MAX_P1 = 25  # Maximum power output of MPPT panel; simply used for axis limits
MAX_P2 = 2.5  # Max P of partial-shading panel; simply used for axis limits
IV_POINTS = 28  # Number of points on I-V curve
MPPT_STEP = 0.1  # Volts
FONT = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}  # Throws warnings and reverts to default font


## Main ##
# Set up gpib and instrument(s) #
gpib  = prologix_serial('/dev/ttyUSB0', timeout=5, debug=False)
try:
    eload = prologix_6060b(gpib, ELOAD_ADDR, 'VOLT', debug=False)
    VDMM = prologix_34461a(gpib, VDMM_ADDR, 'VOLT', maxRange=100, continuous=True, debug=False)
    IDMM = prologix_34461a(gpib, IDMM_ADDR, 'CURR', maxRange=1, continuous=True, debug=False)

    VDMM.waitForTrigger()
    IDMM.waitForTrigger()


    # I-V Sweep #
    eloadVoltage = []
    eloadPower = []

    for sweepVoltage in range(IV_POINTS):  # No native support for
                                           # float step-value
        eload.setValue(sweepVoltage * V_OC/(IV_POINTS-1.0))
        time.sleep(0.1)  # Settling time

        readV = float(eload.readVoltage())
        readI = float(eload.readCurrent())
        eloadVoltage.append(readV)
        eloadPower.append(readV * readI)

    del sweepVoltage


    # Set up plots #
    x1 = 0
    y1 = 0
    power1 = collections.deque()
    power2 = collections.deque()
    times = collections.deque()
    mpl.rc('font', **FONT)
    plt.ion()

    plt.figure(num=1, figsize=(9,9))
    plt.plot(eloadVoltage, eloadPower, 'DarkOrange', linewidth=4)
    p1, = plt.plot(x1, y1, 'ob', markersize=17)  # Not sure why tuple (p1,) is needed
    plt.title('PV Curve')
    plt.xlabel('Voltage (V)')
    plt.ylabel('Power (W)')
    plt.xlim([0, V_OC])
    plt.ylim([0, 1.1*MAX_P1])
    thisManager = plt.get_current_fig_manager()
    thisManager.window.wm_geometry('+300+0')
    plt.draw()

    plt.figure(num=2, figsize=(9,9))
    line1, = plt.plot(times, power1, 'DarkOrange', linewidth=4)  # Not sure why tuple is needed
    plt.title('Panel Power Output')
    plt.xlabel('MPPT Iteration')
    plt.ylabel('Power (W)')
    plt.xlim([0, 100])
    plt.ylim([0, 1.1*MAX_P1])
    thisManager = plt.get_current_fig_manager()
    thisManager.window.wm_geometry('+1030+0')
    plt.draw()

    plt.figure(num=3, figsize=(9,9))
    line2, = plt.plot(times, power2, 'DarkOrange', linewidth=4)  # Not sure why tuple is needed
    plt.title('Panel Power Output')
    plt.xlabel('Sample')
    plt.ylabel('Power (W)')
    plt.xlim([0, 100])
    plt.ylim([0, 1.1*MAX_P2])
    thisManager = plt.get_current_fig_manager()
    thisManager.window.wm_geometry('+665+0')
    plt.draw()


    # Initialize MPPT #
    # Obtain a valid value of flag to start the e-load at; defaults to 0
    with open('flag.dat', 'a+') as f:  # Using a+ so that
                                       # file is created if non-existent
        try:
            f.seek(0)
            flag = float(f.read())
        except:  # In case of non-float
            flag = 0
        else:
            if not(0 <= flag <= V_OC):  # If out of range
                flag = 0
        finally:
            eload.setValue(flag)
            f.truncate(0)  # Clear file to denote idle state

    t = 0
    direction = 1


    # Run #
    while t < 100:
        with open('flag.dat', 'r+') as f:
            # Ignore input unless float and within range
            try:
                flag = float(f.read())
            except:
                pass
            else:
                if 0 <= flag <= V_OC:
                    eload.setValue(flag)
                    f.truncate(0)

        # MPPT
        oldVoltage = float(eload.readVoltage())
        oldCurrent = float(eload.readCurrent())
        oldPower = oldVoltage * oldCurrent
        eload.setValue(oldVoltage + direction*MPPT_STEP)
        newVoltage = float(eload.readVoltage())
        newCurrent = float(eload.readCurrent())
        newPower = newVoltage * newCurrent
        if newPower < oldPower:
            direction *= -1

        # Partial Shading
        # getLastSample() adds extra text at end (e.g. "VDC")
        # Trim string and convert to float
        readV = float(VDMM.getLastSample()[:-5])
        readI = float(IDMM.getLastSample()[:-5])
        readP = readV * readI

        # Update plots
        x1 = newVoltage
        y1 = newPower
        power1.append(newPower)
        power2.append(readP)
        times.append(t)
        t += 1
        p1.set_xdata(x1)
        p1.set_ydata(y1)
        line1.set_xdata(times)
        line1.set_ydata(power1)
        line2.set_xdata(times)
        line2.set_ydata(power2)
        plt.figure(1)
        plt.draw()
        plt.figure(2)
        plt.draw()
        plt.figure(3)
        plt.draw()


    # After 100 iterations, continue MPPT but shift P(t) window
    # to keep plot in view.
    while True:
        with open('flag.dat', 'r+') as f:
            try:
                flag = float(f.read())
            except:
                pass
            else:
                if 0 <= flag <= V_OC:
                    eload.setValue(flag)
                    f.truncate(0)

        # MPPT
        oldVoltage = float(eload.readVoltage())
        oldCurrent = float(eload.readCurrent())
        oldPower = oldVoltage * oldCurrent
        eload.setValue(oldVoltage + direction*MPPT_STEP)
        newVoltage = float(eload.readVoltage())
        newCurrent = float(eload.readCurrent())
        newPower = newVoltage * newCurrent
        if newPower < oldPower:
            direction *= -1

        # Partial Shading
        readV = float(VDMM.getLastSample()[:-5])
        readI = float(IDMM.getLastSample()[:-5])
        readP = readV * readI

        # Update plots
        x1 = newVoltage
        y1 = newPower
        power1.append(newPower)
        power2.append(readP)
        times.append(t)
        power1.popleft()
        power2.popleft()
        times.popleft()
        t += 1
        p1.set_xdata(x1)
        p1.set_ydata(y1)
        line1.set_xdata(times)
        line1.set_ydata(power1)
        line2.set_xdata(times)
        line2.set_ydata(power2)
        plt.figure(1)
        plt.draw()
        plt.figure(2)
        plt.xlim([t-100, t])
        plt.draw()
        plt.figure(3)
        plt.xlim([t-100, t])
        plt.draw()


finally:
    gpib.terminate()

