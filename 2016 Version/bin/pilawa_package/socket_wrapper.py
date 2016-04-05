#Written by Felix Hsiao
#Last edit on 8/19/2013 by Felix Hsiao

import socket

class prologix_socket:
    def __init__(self, host, port=5025, timeout=60, debug=False):
        #Check for host name on device (pass as string); can be IP address or <host>.<domain>
        #Default port is universal for Agilent devices
        self.host = host
        self.port = port
        self.timeout = timeout
        self.debug = debug
        self.sock = None
        self.initialize()

    def initialize(self):
        if self.debug: print 'Connecting to %s on port %d ...' %(self.host, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)

        try:
            self.sock.connect((self.host, self.port))
        except socket.error, e:
            print 'Could not connect to server!'
            print e
            raise RuntimeError('Error connecting to server!')
        
        self.ID = None
        try:
            self.write('*IDN?')
            self.ID = self.readline()
        except socket.error, e:
            if self.debug: print 'Could not read back device ID!'
            print e
            self.terminate()
            raise RuntimeError('Error connecting to server!')

        if self.debug:
            print 'ID:', self.ID
            print 'Socket connected to %s on port %d.' %(self.host, self.port)

    def terminate(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        if self.debug: print 'Closed connection to %s on port %d.' %(self.host, self.port)

    def write(self, data):
    #Not all data may be sent with one send()
        data = data + '\n'
        totalSent = 0
        while totalSent < len(data):
            sent = self.sock.send(data[totalSent:])
            if sent == 0:
                if self.debug: print 'Connection broken. Closing socket...'
                self.terminate()
                raise RuntimeError('Connection broken!')
            else:
                totalSent = totalSent + sent

        if self.debug: print 'Sent:', data

    def read(self, length=1):
    #Not all data may be received with one recv()
        data = ''
        while len(data) < length:
            recv = self.sock.recv(length-len(data))
            if recv == '':
                if self.debug: print 'Connection broken. Closing socket...'
                self.terminate()
                raise RuntimeError('Connection broken!')
            else:
                data = data + recv

        if self.debug: print 'Recv:', data
        return data

    def readline(self):
    #Not all data may be received with one recv()
        data = ''
        while True:
            recv = self.sock.recv(1)
            if recv == '':
                if self.debug: print 'Connection broken. Closing socket...'
                self.terminate()
                raise RuntimeError('Connection broken!')
            else:
                data = data + recv
                if data[len(data)-1]=='\n': break
    
        data = data.strip()
        if self.debug: print 'Recv:', data
        return data

    def set_address(self, addr):
    #Not used; kept for interchangeability with gpib
        if self.debug: 'Ignored set address command.'
        pass

    def trigger_devices(self, devlist=[]):
    #devlist is ignored and omittable; only the associated device is triggered
        self.write('*TRG')
        if self.debug: print 'Triggered %s.' %(self.ID)
