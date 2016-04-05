#Written by Robert Pilawa
#Last edit on ? by ?

class microcontroller_serial_ro:
    def __init__(self, port, baud=9600, debug=True, timeout=60):
        self.port     = port
        self.baudrate = baud
        self.timeout  = timeout
        self.debug    = debug
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
        except SerialException, e:
            print "Error opening the serial port!"
            print e
            raise
        else:
            if self.debug: print "Serial port", self.port, "opened:"
            if self.debug: print self.serial

    def terminate(self):
        self.serial.close()
        if self.debug: print "Closed port:"
        if self.debug: print self.serial
    
    def read(self, length=1):
        data = self.serial.read(size=length)
        if self.debug: print "Recv:", data
        return data
    
    def readline(self):
        data = self.serial.readline().strip()
        if self.debug: print "Recv:", data
        return data
