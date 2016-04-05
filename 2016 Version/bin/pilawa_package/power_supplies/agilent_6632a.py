#Written by Robert Pilawa
#Last edit on ? by Ruichen Zhao

class prologix_6632a:
    def __init__(self, prologix=None, addr=None, mode=None, rang=2, debug=False):
        self.prologix  = prologix
        self.addr     = addr
        self.debug    = debug
        self.value = 0
        self.initialize()
    
    def initialize(self):
        self.prologix.set_address(self.addr) # address the proper instrument
        self.prologix.write("CLR")
        self.prologix.write("OUT 0")
    
    def setVoltage(self, value=None):
        self.value=value
        self.prologix.set_address(self.addr)
        self.prologix.write("VSET %s" % self.value )
    def setCurrent(self, value=None):
        self.value=value
        self.prologix.set_address(self.addr)
        self.prologix.write("ISET %s" % self.value )
    def readVoltage(self):
        self.prologix.set_address(self.addr)
        self.prologix.write("VOUT?")
        data = self.prologix.readline()
        return data
    
    def readCurrent(self, value=None):
        self.prologix.set_address(self.addr)
        self.prologix.write("IOUT?")
        data = self.prologix.readline()
        return data
    
    def activate(self):
        self.prologix.set_address(self.addr)
        self.prologix.write("OUT 1")
    def deactivate(self):
        self.prologix.set_address(self.addr)
        self.prologix.write("OUT 0")
    def default_setting(self):
        self.prologix.set_address(self.addr)
        self.prologix.write("CLR")
