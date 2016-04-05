#Written by Robert Pilawa
#Last edit on ? by ?

import serial

class prologix_serial:
    def __init__(self, port, baud=115200, debug=False, lineterm='\n', timeout=60):
        self.port     = port
        self.baudrate = baud
        self.timeout  = timeout
        self.debug    = debug
        self.lineterm = lineterm
        self.serial   = None
        self.initialize()
    
    def initialize(self):
        if self.serial:
            if self.serial.isOpen(): self.terminate()
        
        self.serial          = serial.Serial()
        self.serial.port     = self.port
        self.serial.baudrate = self.baudrate
        self.serial.timeout  = self.timeout
        
        try:
            self.serial.open()
        except serial.SerialException, e:
            print "Error opening the serial port!"
            print e
            raise
        else:
            if self.debug: print "Serial port", self.port, "opened:"
            if self.debug: print self.serial
        
        # Try to read back the prologix controller version to
        #  verify that serial communication works
        if self.debug: print "Fetching controller version..."
        self.write("")
        self.write("++ver")
        version = self.readline()
        if self.debug: print "Ver :", version
        if version == '':
            print "Could not read back controller version!"
            self.terminate()
        self.write("++auto 0") #if 1, issue instrument to talk. This will cause errors if a command such as *CLS is sent, which doesn't require an answer. Can manually read instrument with ++read eoi instead if want to.
        self.write("++eoi 1") #if 1, enables assertion of the EOI signal with the last character sent. Some instruments require this
        self.write("++eos 3")#EOS termination character 0-CR+LF, 1-CR, 2-LF, 3 - None

    def terminate(self):
        self.serial.close()
        if self.debug: print "Closed port:"
        if self.debug: print self.serial
    
    def write(self, data):
        self.serial.write(data+self.lineterm)
        if self.debug: print "Sent:", data
    
    def read(self, length=1):
        data = self.serial.read(size=length)
        if self.debug: print "Recv:", data
    
    def readline(self):
        self.write("++read 10")
        data = self.serial.readline().strip()
        if self.debug: print "Recv:", data
        return data
    
    def set_address(self, addr):
        self.write("++addr %d" % addr)
    
    def trigger_devices(self,devlist):
        self.write("++trg " + " ".join([str(x) for x in devlist]) )
