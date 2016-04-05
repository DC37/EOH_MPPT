#Written by Robert Pilawa
#Last edit on 12/2/2013 by Felix Hsiao

import time

class prologix_2400:
    def __init__(self, prologix, addr, NPLC=None, trigDel=None, sourDel=None, autoZero=True, continuous=False, debug=False):
        self.prologix = prologix
        self.addr = addr
        self.NPLC = NPLC  #DEF=1, MIN=0.01, MAX=10
        self.trigDel = trigDel  #Trigger delay; sample period = trigDel + sourDel + measurement time; DEF=0, MAX=999.9999 s
        self.sourDel = sourDel  #Source delay; settling time between sourcing and measurement; MIN=1 ms, MAX=999.9999 s; default is auto delay
        self.autoZero = autoZero
        self.continuous = continuous
        self.debug = debug
        self.initialize()
    
    def initialize(self):
        if self.debug: print 'Initializing address %d ...' %(self.addr)
        self.prologix.set_address(self.addr) # address the proper instrument
        if self.debug: print 'Reset'
        self.prologix.write('*RST')
        if self.debug: print 'Clear'
        self.prologix.write('*CLS')
        if self.debug: print 'Setup concurrent measurement'
        self.prologix.write('FUNC:CONC 1')
        self.prologix.write('FUNC "VOLT", "CURR"')
        self.prologix.write("FORM:ELEM VOLT, CURR") #setup to read back voltage, current
        if self.debug: print 'Enable auto output-off'
        self.prologix.write('SOUR:CLE:AUTO 1')  #Sources only when measuring
        if self.NPLC is not None:
            if self.debug: print 'Set NPLC'
            self.prologix.write('VOLT:NPLC %s' %(self.NPLC))  #Global; all measurements have same NPLC
        if self.debug and not (self.trigDel is None and self.sourDel is None): print 'Setup triggering'
        if self.trigDel is not None:
            self.prologix.write('TRIG:DEL %s' %(self.trigDel))
        if self.sourDel is not None:
            self.prologix.write('SOUR:DEL %s' %(self.sourDel))  #Automatically disables auto delay
        if self.debug: print 'Setup arming'
        self.prologix.write('ARM:SOUR BUS')  #ARM analogous to triggers, TRIG analogous to samples
        if self.continuous:
            self.prologix.write('ARM:COUN INF')
        if not self.autoZero:
            if self.debug: print 'Disable auto-zero'
            self.prologix.write('SYST:AZER:STAT OFF')
        if self.debug: print 'Address %d initialized.' %(self.addr)

    def setSource(self, mode, value, cmpl=None, samples=None):
        #Note: this will not automatically turn on output
        #DC output; mode is VOLT or CURR
        #cmpl is compliance, or limit for non-sourced mode (e.g. current limit in voltage mode)
        if self.debug: print 'Setting up DC sourcing for address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        if self.debug: print 'Set source mode'
        self.prologix.write('SOUR:FUNC %s' %(mode))
        if self.debug: print 'Set sourcing mode'
        self.prologix.write('SOUR:%s:MODE FIX' %(mode))
        if self.debug: print 'Set value'
        self.prologix.write('SOUR:%s %s' %(mode, value))
        if cmpl is not None:
            if mode.upper()=='VOLT':
                self.prologix.write('CURR:PROT %s' %(cmpl))
            elif mode.upper()=='CURR':
                self.prologix.write('VOLT:PROT %s' %(cmpl))
        if samples is not None:
            if self.debug: print 'Setup triggering'
            self.prologix.write('TRIG:COUN %s' %(samples))
        if self.debug: print 'Address %d sourcing configured.' %(self.addr)

    def configSweep(self, mode, value1, value2, centered=False, cmpl=None, points=2500, type=None):
        #Mode is VOLT or CURR
        #cmpl is compliance, or limit for non-sourced mode (e.g. current limit in voltage mode)
        if self.debug: print 'Setting up sweep for address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('SOUR:%s:MODE SWE' %(mode))
        if not centered:  #value1 and value2 are start and stop points
            if self.debug: print 'Set endpoints'
            self.prologix.write('SOUR:%s:STAR %s' %(mode, value1))
            self.prologix.write('SOUR:%s:STOP %s' %(mode, value2))
        else:  #value1 is center frequency, value2 is total span
            if self.debug: print 'Set center and span'
            self.prologix.write('SOUR:%s:CENT %s' %(mode, value1))
            self.prologix.write('SOUR:%s:SPAN %s' %(mode, value2))
        if cmpl is not None:
            if mode.upper()=='VOLT':
                self.prologix.write('CURR:PROT %s' %(cmpl))
            elif mode.upper()=='CURR':
                self.prologix.write('VOLT:PROT %s' %(cmpl))
        if points!=2500:  #DEF=MAX=2500, but please use an integer
            if self.debug: print 'Set number of points'
            self.prologix.write('SOUR:SWE:POIN %d' %(points))
        if type is not None:  #Can be LINear or LOGarithmic; default linear
            if self.debug: print 'Set sweep type'
            self.prologix.write('SOUR:SWE:SPAC %s' %(type))
        if self.debug: print 'Setup triggering'
        self.prologix.write('TRIG:COUN %d' %(points))
        if self.debug: print 'Address %d sweep mode configured.' %(self.addr)

    def configList(self, mode, list):
        #list must be a list of numbers
        if self.debug: print 'Setting up list sourcing for address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('SOUR:%s:MODE LIST')
        self.prologix.write('SOUR:LIST:%s %s' %(mode, str(list)[1:-1]))
        if self.debug: print 'Setup triggering'
        self.prologix.write('TRIG:COUN %d' %(len(list)))
        if self.debug: print 'Address %d list mode configured.' %(self.addr)

    def waitForTrigger(self):
        if self.debug: print 'Preparing address %d for triggering ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('INIT')
        if self.debug: print 'Address %d waiting for trigger.' %(self.addr)
    
    def readData(self, wait=0.1):
        time.sleep(wait)  #Wait until measurement finishes
        if self.debug: print 'Fetching data from address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('FETC?')
        data = self.prologix.readline()
        if self.debug: print 'Recv:', data
        return data

    def readData2(self, maxReadings=2500):  #Reads and erases up to maxReadings starting from oldest first; can read during measurement (useful for continuous measurement); see SCPI reference for syntax
        if self.debug: print 'Reading data from address %d ...' %(self.addr)
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


    #Auto output-off enabled; use following for manual sourcing
    def activate(self):
        if self.debug: print 'Starting output from address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('OUTP ON')
        if self.debug: print 'Address %d output on.' %(self.addr)
    
    def deactivate(self):
        if self.debug: print 'Stopping output from address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('OUTP OFF')
        if self.debug: print 'Address %d output off.' %(self.addr)


    def checkError(self):
        if self.debug: print 'Checking if error was generated by address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('SYST:ERR?')
        time.sleep(0.01)
        data = self.prologix.readline()
        if self.debug: print 'Recv:', data
        return data
