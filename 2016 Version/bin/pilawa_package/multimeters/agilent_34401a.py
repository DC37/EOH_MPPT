#Written by Robert Pilawa
#Last edit on ? by ?

class prologix_34401a:
    def __init__(self, prologix=None, addr=None, mode=None, maxrange=None, nplc=None, debug=False):
        self.prologix  = prologix
        self.addr     = addr
        self.mode     = mode
        self.maxrange = maxrange or "DEF"
        self.nplc     = nplc
        self.debug    = debug
        self.initialize()
    
    def initialize(self):
        # Configure DC measurement (Agilent 34401a)
        # port: serial.Serial()
        # meas: string ("VOLT"|"CURR")
        if self.debug: print "Initializing %d for %s" % (self.addr, self.mode)
        self.prologix.set_address(self.addr) # address the proper instrument
        self.prologix.write("*RST") # reset the meter to its power-on state
        self.prologix.write("*CLS") # clear the status registers
        self.prologix.write("CONF:%s:DC %s,DEF" % (self.mode,self.maxrange))
        if self.nplc: self.prologix.write("%s:DC:NPLC %s" % (self.mode, self.nplc))
        self.prologix.write("zero:auto on") # off,once,on
        self.prologix.write("trig:del 0")
        self.prologix.write("TRIG:SOUR BUS") # bus triggering
        self.prologix.write("TRIG:COUN 1") # one trigger per init cycle
    
    def waitForTrigger(self):
        self.prologix.set_address(self.addr)
        self.prologix.write("INIT")
    
    def readData(self):
        # Read back the data
        if self.debug: print "Fetching data from %d:" % self.addr
        self.prologix.set_address(self.addr) # select device
        self.prologix.write("FETC?") # fetch value
        data = self.prologix.readline() # read until LF (ascii 10)
        if self.debug: print "Recv:", data
        return data
