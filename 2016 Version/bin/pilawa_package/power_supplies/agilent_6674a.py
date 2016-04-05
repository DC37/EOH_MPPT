#Written by Ruichen Zhao ruichen77@gmail.com
#Last edit on ? by Ruichen Zhao

'''
    NOTICE:
    By default setting HP6674A is using SCPI Command,
    different from APRS command used by HP6632A
    SCPI has slightly more complicated functions
    may use SYST:LANG switch between two different language
    '''

class prologix_6674a:
    
    def __init__(self, prologix=None, addr=None, mode=None, rang=2, debug=False):
        self.prologix  = prologix
        self.addr     = addr
        self.debug    = debug
        self.value = 0
        self.initialize()
    
    def initialize(self):
        if self.debug:print "prologix_HP6674A:initialize power supply "
        self.prologix.set_address(self.addr) # address the proper instrument
        if self.debug:print "reset\n"
        self.prologix.write("*RST")
        if self.debug:self.err()
        if self.debug:print "turn off power supply\n"
        self.prologix.write("OUTP:STAT OFF")
        if self.debug:self.err()
    
    
    def setVoltage(self, value=None):
        if self.debug:print "prologix_HP6674A:setting voltage"
        self.value=value
        self.prologix.set_address(self.addr)
        self.prologix.write("VOLT %s" % self.value )
        
        if self.debug:
            self.err()
            self.prologix.write("VOLT?")
            print "Voltage set to:", self.prologix.readline(),"\n"
    
    def setCurrent(self, value=None):
        if self.debug:print "prologix_HP6674A:setting current"
        self.value=value
        self.prologix.set_address(self.addr)
        self.prologix.write("CURR %s" % self.value )
        if self.debug:
            self.err()
            self.prologix.write("CURR?")
            print "Current set to:", self.prologix.readline(),"\n"
    
    def readVoltage(self):
        self.prologix.set_address(self.addr)
        self.prologix.write("MEAS:VOLT?")
        data = self.prologix.readline()
        return data
    
    def readCurrent(self, value=None):
        self.prologix.set_address(self.addr)
        self.prologix.write("MEAS:CURR?")
        data = self.prologix.readline()
        return data
    
    def activate(self):
        self.prologix.set_address(self.addr)
        self.prologix.write("OUTP:STAT ON")
    def deactivate(self):
        self.prologix.set_address(self.addr)
        self.prologix.write("OUTP:STAT OFF")
    
    def default_setting(self):
        self.prologix.set_address(self.addr)
        self.prologix.write("*RST")
    
    def err(self):
        self.prologix.set_address(self.addr)
        self.prologix.write("SYST:ERR?")
        print "Error?",self.prologix.readline(),"\n"