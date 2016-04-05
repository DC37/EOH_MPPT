#Written by Robert Pilawa
#Last edit on 8/19/2013 by Felix Hsiao

class prologix_6060b:
    def __init__(self, prologix=None, addr=None, mode=None, rang=2, debug=False):
        self.prologix  = prologix
        self.addr     = addr
        self.mode     = mode
        self.rang    = rang
        self.debug    = debug
        self.value = 0
        self.initialize()
    
    def initialize(self):
        if self.debug: print "Initializing %d for %s" % (self.addr, self.mode)
        self.prologix.set_address(self.addr) # address the proper instrument
        if self.debug: print "Issuing *cls"
        self.prologix.write("*cls")
        self.setMode(self.mode, self.rang) #set mode and range
        if self.debug: print "Issuing trig:imm"
        self.prologix.write("trig:imm")
    
    def setSlew(self, value=None):
        self.prologix.set_address(self.addr) # address the proper instrument
        if self.debug: print "Address %d issued %s:SLEW %s" % (self.addr, self.mode, self.value)
        self.prologix.write("%s:SLEW %s" % (self.mode, self.value) )
    
    def setMode(self, mode=None, rang=None):
        #Mode can be CURR, VOLT, RES
        self.mode=mode
        self.prologix.set_address(self.addr) # address the proper instrument
        if self.debug: print "Address %d issued MODE:%s" % (self.addr, self.mode)
        self.prologix.write("MODE:%s" % self.mode)
    
    def setValue(self, value=None):
        self.value=value
        self.prologix.set_address(self.addr) # address the proper instrument
        #self.prologix.write("%s %s") % (self.mode, value)
        if self.debug: print "Address %d issued %s %s" % (self.addr, self.mode, self.value)
        self.prologix.write("%s %s" % (self.mode, self.value) )
    
    def readCurrent(self):
        # Read back the data, originally tried fetch here, but read works better as it also initiates the meter
        if self.debug: print "Fetching data from %d:" % self.addr
        self.prologix.set_address(self.addr) # select device
        self.prologix.write("MEAS:CURR?") # fetch value
        data = self.prologix.readline() # read until LF (ascii 10)
        if self.debug: print "Recv:", data
        return data
    
    def readVoltage(self):
        # Read back the data, originally tried fetch here, but read works better as it also initiates the meter
        if self.debug: print "Fetching data from %d:" % self.addr
        self.prologix.set_address(self.addr) # select device
        self.prologix.write("MEAS:VOLT?") # fetch value
        data = self.prologix.readline() # read until LF (ascii 10)
        if self.debug: print "Recv:", data
        return data
