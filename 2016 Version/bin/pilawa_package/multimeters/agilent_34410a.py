#Written by Felix Hsiao
#Last edit on 2/25/2014 by Josiah McClurg

import time
import math
import struct

class prologix_34410a:
    def __init__(self, prologix, addr, mode='VOLT', ACDC='DC', maxRange='DEF', NPLC=None, samples=None, sampPer=None, autoZero=True, continuous=False, debug=False):
        self.prologix = prologix
        self.addr = addr
        self.mode = mode.upper()  #Mode can be VOLT, CURR, RES
        self.ACDC = ACDC.upper()
        self.maxRange = maxRange  #Recommended for range to be set manually
        self.NPLC = NPLC  #Can be 0.006, 0.02, 0.06, 0.2, 1, 2, 10, or 100; default 1
        self.samples = samples  #Max=50,000
        self.sampPer = sampPer  #Sample period; MAX=3,600 seconds;
                                #For NPLC=0.006, auto-range off, auto-zero off: sample rate ~ 10,000 samples per second
                                #Default is MIN~0.1 ms (NPLC/60)
        self.autoZero = autoZero
        self.continuous = continuous  #Continuous measurement
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
            if self.sampPer:
                self.prologix.write('SAMP:SOUR TIM')
                self.prologix.write('SAMP:TIM %s' %(self.sampPer))
        if self.debug: print 'Setup triggering'
        if self.continuous:
            self.prologix.write('TRIG:SOUR IMM')
            self.prologix.write('TRIG:COUN INF')
        else:
            self.prologix.write('TRIG:SOUR BUS')
        self.prologix.write('TRIG:DEL 0')
        if self.debug: print 'Address %d initialized.' %(self.addr)

    def waitForTrigger(self):
        if self.debug: print 'Preparing address %d for triggering ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('INIT')
        if self.debug: print 'Address %d waiting for trigger.' %(self.addr)

    def readData(self, wait=1.1): #Experimental wait time ~ samples*NPLC/60+1
        time.sleep(wait)  #Wait until measurement finishes
        if self.debug: print 'Fetching data from address %d ...' %(self.addr)
        self.prologix.set_address(self.addr)
        self.prologix.write('FETC?')
        data = self.prologix.readline()
        if self.debug: print 'Recv:', data
        return data

    def readData2(self, maxReadings=50000):  #Reads and erases up to maxReadings starting from oldest first; can read during measurement (useful for continuous measurement); see SCPI reference for syntax
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

    # Sets the device waiting for a trigger. In IMM mode, this starts the samples
    def continuousSampleWaitForTrigger(self):
        self.prologix.write('INIT')

    # Reads and empties the memory buffer. May return an empty list if you read too quickly.
    def continuousSampleRead(self):
        sock = self.prologix

        # Tell the device to read and empty the memory buffer
        sock.write('R?')

        # Reads #d, where d is the number of digits of the length specifier
        lenlen = sock.read(2)

        # Reads the length specifier
        length = int(sock.read(int(lenlen[1])))

        # Reads the binary data
        a = sock.read(length)

        # Get rid of the carriage return from the output buffer
        sock.readline()

        # The data is stored most significant byte first (big endian) as 64 bit float (double)
        s = [struct.unpack('>d',a[i*8:(1+i)*8])[0] for i in range(0,len(a)/8)]
        return s

    def continuousSampleStop(self):
        self.prologix.write('ABOR')

    # Reads the memory buffer at time increments specified by blockSize and triggerTime until numSamples is reached.
    def continuousSampleReadUntil(self,numSamples):
        data = [0]*numSamples
        offset = 0

        # Note how these are divided by two for safety
        triggersTillOverflow = 50000.0/float(2*self.blockSize)
        timeTillOverflow = triggersTillOverflow*self.triggerTime

        while(offset < numSamples):
            s = self.continuousSampleRead()
            if(offset+len(s) <= numSamples):
                data[offset:offset+len(s)] = s
                offset = offset + len(s)
            else:
                data[offset:numSamples] = s[0:numSamples-offset]
                offset = offset + len(s)

            if(offset < numSamples):
                triggersNeeded = float(numSamples-offset)/float(self.blockSize)
                timeTillFinished = triggersNeeded*self.triggerTime

                if(timeTillFinished < timeTillOverflow):
                    if(self.debug):
                        print('Will be done in %g seconds (%d samples left)'%(timeTillFinished,numSamples-offset))
                    time.sleep(timeTillFinished)
                else:
                    if(self.debug):
                        print('Sleeping for %g seconds (%d samples left)'%(timeTillOverflow,numSamples-offset))
                    time.sleep(timeTillOverflow)
            else:
                if(self.debug):
                    print('Continuous sample finished')

        self.continuousSampleStop()
        return data
    
    # triggerMode={'EXT',  # Use the back panel external trigger. Rising slope. Blocksize per trigger
    #              'BUS',  # Use the *TRG signal from the bus. Blocksize samples per trigger.
    #              'IMM'   # Continous trigger.
    # }
    #
    # 1 <= blockSize <= 50000  # Default is 1 if triggerMode is 'EXT'
    #                          # Default is 1 if triggerMode is 'BUS'
    #                          # Default is 50000 if triggerMode is 'IMM'
    #                          #    Note that in this case, there's really no need to change blockSize
    #
    # measType={VOLT:DC,CURR:DC}
    #
    # rang=(if measType=CURR:DC){'3',   '1',  '0.1','0.01','0.001','0.0001'}
    #      (if measType=VOLT:DC){'1000','100','10', '1',   '0.1'}
    #
    # 0.0001 < sampleTime    # Expected minimum sample time. Used to set the integration time for all
    #                        # trigger modes and the inter-sample time when blockSize > 1
    #
    # sampleTime <= triggerTime*blockSize # Expected average trigger time. Used to calculate Defaults to sampleTime*blockSize
    def initializeContinuousSample(self,measType, rang, blockSize=None, triggerMode='IMM', sampleTime=0.0001, triggerTime=None):
        if(measType not in ['VOLT:DC','CURR:DC']):
           raise Exception('Measurement type "%s" not implemented'%(measType))

        rang = '%s'%(rang)
        if((measType == 'VOLT:DC') and (rang not in ['1000','100','10', '1', '0.1'])):
            raise Exception('Invalid range for VOLT:DC')

        if((measType == 'CURR:DC') and (rang not in ['3', '1', '0.1','0.01','0.001','0.0001'])):
            raise Exception('Invalid range for CURR:DC')

        if(triggerMode not in ['EXT','IMM','BUS']):
            raise Exception('Invalid trigger mode')

        if(blockSize == None):
            if(triggerMode in ['EXT','BUS']):
                blockSize = 1
            else:
                blockSize = 50000
        elif((blockSize < 1) or (blockSize > 50000)):
            raise Exception('Block size out of range')

        if(triggerTime == None):
            triggerTime = sampleTime*blockSize
        elif(triggerTime < sampleTime*blockSize):
            raise Exception('Trigger time cannot be less than the minimum sample time')

        sock = self.prologix

        # Clear previous nonsense.
        sock.write('*RST')
        sock.write('*CLS')

        # 64 bit binary transfer mode, MSB first.
        sock.write('FORM:DATA REAL')
        sock.write('FORM:BORD NORM')

        # Don't return to idle state after trigger.
        sock.write('TRIG:COUN INF')
        sock.write('TRIG:SOUR %s'%(triggerMode))
        if(triggerMode == 'EXT'):
            sock.write('TRIG:SLOP POS')

        # Zero delay between trigger and measurement.
        sock.write('TRIG:DEL 0')

        sock.write('SENS:FUNC:ON "%s"'%(measType))

        sock.write('SENS:%s:RANG:AUTO OFF'%(measType))
        sock.write('SENS:%s:RANG:UPP %s'%(measType,rang))

        # The goal is ostensibly to measure voltages quickly, so let's sacrifice some noise immunity
        #sock.write('SENS:%s:ZERO:AUTO ONCE'%(measType))
        sock.write('SENS:%s:ZERO:AUTO OFF'%(measType))

        if(measType == 'VOLT:DC'):
            sock.write('SENS:%s:IMP:AUTO ON'%(measType))

        # The goal is to get as much accuracy for the specified sample time as possible within the device limits
        sock.write('SENS:%s:APER:ENAB ON'%(measType))
        sock.write('SENS:%s:APER? MIN'%(measType))
        minAperTime = float(sock.readline())

        if(sampleTime > minAperTime):
            sock.write('SENS:%s:APER? MAX'%(measType))
            maxAperTime = float(sock.readline())

            if(sampleTime < maxAperTime):
                sock.write('SENS:%s:APER %g'%(measType,sampleTime))
                sock.write('SENS:%s:APER?'%(measType))
                aperTime = float(sock.readline())
            else:
                sock.write('SENS:%s:APER MAX'%(measType))
                aperTime = maxAperTime
        else:
            sock.write('SENS:%s:APER MIN'%(measType))
            aperTime = minAperTime

        if(self.debug):
            print('Integration time: %g'%(aperTime))

            sock.write('SENS:%s:RES?'%(measType))
            resolution = float(sock.readline())
            print("Resolution: %g %s"%(resolution, measType))

        # Number of total samples to take per trigger is specified by blockSize
        sock.write('SAMP:COUN %d'%(blockSize))
        if(self.debug):
            print("Per-trigger sample count: %d"%(blockSize))
        
        if(blockSize > 1):
            # Sample at the specified fixed interval as long as it fits within the limits
            sock.write('SAMP:SOUR TIM')
            sock.write('SAMP:TIM? MIN')
            minSampleTime = float(sock.readline())

            if(sampleTime > minSampleTime):
                sock.write('SAMP:TIM? MAX')
                maxSampleTime = float(sock.readline())

                if(sampleTime < maxSampleTime):
                    sock.write('SAMP:TIM %g'%(sampleTime))
                    sock.write('SAMP:TIM?')
                    actualSampleTime = float(sock.readline())
                else:
                    sock.write('SAMP:TIM MAX')
                    actualSampleTime = maxSampleTime
            else:
                sock.write('SAMP:TIM MIN')
                actualSampleTime = minSampleTime

            self.sampleTime = actualSampleTime
            if(triggerTime < actualSampleTime*blockSize):
                raise Exception('Due to quantization of device, trigger time must be >= %g'%(actualSampleTime*blockSize))

            if(self.debug):
                print('Desired sample time: %g vs Actual sample time: %g'%(sampleTime,actualSampleTime))
        else:
            self.sampleTime = sampleTime
            if(self.debug):
                print('Sample time ignored. One sample per trigger')

        self.triggerTime = triggerTime
        self.blockSize = blockSize
        self.triggerMode = triggerMode

        if(self.debug):
            print('Finished initializing continuous sample')
