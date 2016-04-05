#Written by Ziming Chen
#Last edit on 10/11/2013 by Felix Hsiao

import time

class prologix_34970a:
    def __init__(self, prologix=None, addr=None, mode=None, maxrange='DEF', nplc=None, period=None, samples=None, debug=False):
        self.prologix = prologix
        self.addr     = addr
        self.mode     = mode
        self.maxrange = maxrange or "DEF"
        self.nplc     = nplc
        self.period   = period
        self.samples  = samples
        self.debug    = debug
        self.initialize()

    def initialize(self):
        if self.debug: print "Initializing %s for %s" % (self.addr, self.mode)
        self.prologix.set_address(self.addr)
        self.prologix.write("*RST")
        self.prologix.write("*CLS")
        self.prologix.write("CONF:%s:DC %s,(@101,102,103,104)" % (self.mode,self.maxrange))
        #self.prologix.write("ROUT:SCAN (@101,103)")
        if self.nplc:
           self.prologix.write("%s:DC:NPLC %s" % (self.mode,self.nplc))
        if self.samples is not None:
           self.prologix.write("TRIG:COUN %s" % (self.samples))
           self.prologix.write("TRIG:SOUR TIM")
           if self.period is not None:           
                self.prologix.write("TRIG:TIM %s" % (self.period))
        else:
           self.prologix.write("TRIG:SOUR BUS")

    def waitForTrigger(self):
        self.prologix.set_address(self.addr)
        self.prologix.write("INIT")
        if self.debug: print "waitForTrigger"

    def checkError(self):
        if self.debug: print "Error at address %s" %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write("SYST:ERR?")
        time.sleep(0.1)
        data = self.prologix.readline()
        if self.debug: print "Receive", data
        return data

    def setScanList(self, ScanList):
        self.prologix.set_address(self.addr)
        self.prologix.write("ROUT:SCAN (@%s)" %(ScanList))

    def readData(self):
        # Read back the data
        if self.debug: print "Fetching data from %s:" % self.addr
        self.prologix.set_address(self.addr) # select device
        self.prologix.write("FETC?") # fetch value
        data = self.prologix.readline() # read until LF (ascii 10)
        if self.debug: print "Recv:", data
        return data
