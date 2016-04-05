# Adapted from Josiah Mcclurg`s code "fluke45.py",
# Written by Ruichen Zhao ruichen77@gmail.com
# Last edit on ? by Ruichen Zhao

class prologix_FLUKE45:
    def __init__(self, prologix=None, addr=None, mode=None, maxrange=None, nplc=None, debug=False):
        self.prologix  = prologix  ##prologix
        self.addr     = addr
        self.mode     = mode
        self.maxrange = maxrange or "DEF"
        self.nplc     = nplc
        self.debug    = debug
        self.initialize()
    
    def initialize(self):
        # please be aware that the baud rate and timeout can
        # actually be set to any reasonable value.
        
        # clear interface in case it is still responding to old commands
        if self.debug: print("initialize device");
        self.prologix.set_address(self.addr) # address the proper instrument
        self.prologix.write("*CLS\n")
        self.prologix.write("++ifc\n")
        
        # ensure that connection was successfull
        self.prologix.write("++spoll\n")
        response = self.prologix.readline().strip()
        self.prologix.write("%s\n"% (self.mode))
        self.prologix.write("AUTO\n")
        self.prologix.write("RATE S\n")
        if self.debug:
            print("Device responded with: '%s'"%(response))
    
    def setMode(self, mode):
        # set device address
        self.prologix.set_address(self.addr) # address the proper instrument
        #   self.prologix.write("++addr %d\n"%(self.addr))
        self.prologix.write("%s\n"% (mode))
        self.prologix.write("AUTO\n")
    
    def getMeasurement(self):
        # set device address
        self.prologix.set_address(self.addr) # address the proper instrument
        
        #    self.prologix.write("++addr %d\n"%(self.addr))
        # request the voltage
        self.prologix.write("MEAS1?\n")
        
        # read until you see the End Or Identify character
        self.prologix.write("++read eoi\n")
        response = self.prologix.readline().strip()
        if self.debug: print("response: #%s#\n"%response)
        return float(response)
    
    def waitForTrigger(self):
        self.prologix.set_address(self.addr)
        self.prologix.write("TRIGGER 2")
    
    def readData(self):
        # Read back the data
        if self.debug: print "Fetching data from %d:" % self.addr
        self.prologix.set_address(self.addr) # select device
        self.prologix.write("VAL?") # fetch value request
        self.prologix.write("++read eoi\n")
        response = self.prologix.readline().strip()
        if self.debug: print("response: #%s#\n"%response)
        return response
    
    def triggerType(self):
        self.prologix.write("TRIGGER?")
        time.sleep(0.1)
        if self.debug: print "Recv:", self.prologix.readline()