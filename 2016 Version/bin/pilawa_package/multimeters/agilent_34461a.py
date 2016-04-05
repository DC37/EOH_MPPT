#Written by Felix Hsiao
#Last edit on 1/26/2014 by Felix Hsiao

import time

class prologix_34461a:
    def __init__(self, prologix, addr, mode='VOLT', ACDC='DC', maxRange='DEF', NPLC=None, samples=None, sampPer=0, autoZero=True, continuous=False, debug=False):
        self.prologix = prologix
        self.addr = addr
        self.mode = mode.upper()  #Mode can be VOLT, CURR, RES
        self.ACDC = ACDC.upper()
        self.maxRange = maxRange  #Recommended for range to be set manually
        self.NPLC = NPLC  #Default 10
        self.samples = samples  #MAX=1,000,000, but memory can only store 10,000; set >10,000 for continuous measurement
        self.sampPer = sampPer  #Sample period, which is added to the intrinsic sampling time;
                                #MAX=3,600 seconds;
                                #For NPLC=0.02, auto-range off, auto-zero off: sample rate ~ 1100 samples per second;
                                #Intrinsic sample time ~ NPLC/22;
        self.autoZero = autoZero
        self.continuous = continuous
        self.debug = debug
        self.initialize()

    def initialize(self):
        if self.debug: print 'Initializing address %d for measuring %s %s ...' %(self.addr, self.ACDC, self.mode)
        self.prologix.set_address(self.addr)
        if self.debug: print 'Reset'
        self.prologix.write('*RST')
        if self.debug: print 'Clear'
        self.prologix.write('*CLS')
        if self.debug: print 'Configure'
        if self.mode=='RES':
            self.prologix.write('CONF:%s %s' %(self.mode, self.maxRange))
        else:
            self.prologix.write('CONF:%s:%s %s' %(self.mode, self.ACDC, self.maxRange))
            if not(self.autoZero): self.prologix.write('%s:ZERO:AUTO OFF' %(self.mode))
        if self.NPLC is not None:
            if self.debug: print 'Set NPLC'
            if self.ACDC=='DC':
                self.prologix.write('%s:NPLC %f' %(self.mode, self.NPLC))
            else:
                print('Cannot set NPLC for this configuration.')
        if self.samples is not None:
            if self.debug: print 'Setup sampling'
            self.prologix.write('SAMP:COUN %s' %(self.samples))
        if self.debug: print 'Setup triggering'
        if self.continuous or self.samples>10000:  #Assuming continuous measurement desired
            self.prologix.write('TRIG:SOUR IMM')
            self.prologix.write('TRIG:COUN INF')
        else:
            self.prologix.write('TRIG:SOUR BUS')
        self.prologix.write('TRIG:DEL %s' %(self.sampPer))  #model has no SAMP:DEL
        if self.debug: print 'Address %d initialized.' %(self.addr)

    def waitForTrigger(self):
        if self.debug: print 'Preparing address %d for triggering ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('INIT')
        if self.debug: print 'Address %d waiting for trigger.' %(self.addr)

    def readData(self, wait=1.5): #Experimental wait time ~ samples*(sampPer+NPLC/22)+1
        time.sleep(wait)  #Wait until measurement finishes
        if self.debug: print 'Fetching data from address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('FETC?')
        data = self.prologix.readline()
        if self.debug: print 'Recv:', data
        return data
    
    def readData2(self, maxReadings=10000):  #Reads and erases up to maxReadings starting from oldest first; can read during measurement (useful for continuous measurement); see SCPI reference for syntax
        if self.debug: print 'Reading data from address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('R? %d' %(maxReadings))
        data = self.prologix.readline()
        if self.debug: print 'Recv:', data
        return data
    
    def getLastSample(self):
        if self.debug: print 'Fetching most recent sample from address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('DATA:LAST?')
        data = self.prologix.readline()
        if self.debug: print 'Recv:', data
        return data
    
    def abort(self):  #Cancel INIT or current measurement(s) (useful for continuous measurement)
        if self.debug: print 'Aborting address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('ABOR')
        if self.debug: print 'Aborted.'

    def countData(self):  #For testing purposes; note that each trigger overwrites previous measurements
        if self.debug: print 'Checking number of data points stored in address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('DATA:POIN?')
        time.sleep(0.01)
        points = self.prologix.readline()
        if self.debug: print 'Recv:', points
        return points

    def clearData(self):  #For testing gpib; note that each trigger overwrites previous measurements; do not use with socket as it will time out
        if self.debug: print 'Clearing data stored in address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('R?')
        time.sleep(0.01)
        junk = self.prologix.readline()
        if self.debug: print junk
        while junk != '':  #Clear prologix memory
            junk = self.prologix.readline()
            if self.debug: print junk

        if self.debug: print 'Address %d data cleared.' %(self.addr)

    def checkError(self):
        if self.debug: print 'Checking if error was generated by address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('SYST:ERR?')
        time.sleep(0.01)
        data = self.prologix.readline()
        if self.debug: print 'Recv:', data
        return data
