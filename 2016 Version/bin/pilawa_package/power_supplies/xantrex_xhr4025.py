#Written by Josiah McClurg
#Last edit on 8/23/2013 by Felix Hsiao

# Note: This code assumes the use of a PROLOGIX GPIB to USB
# controller configured in serial mode, and that the device
# is set to enter remote mode and issue a service request on
# startup.

# For information on the GPIB controller, please reference
# http://prologix.biz/gpib-usb-controller.html

# For information on the GPIB commands for this device, see
# http://www.atecorp.com/ATECorp/media/pdfs/data-sheets/Xantrex-XHR-Series_Manual.pdf
class prologix_xhr4025:
		def __init__(self, comPort=None, addr=None, debug=False):
			# please be aware that the baud rate and timeout can
			# actually be set to any reasonable value.
			self.comPort = comPort
			self.addr = addr


			# clear interface in case it is still responding to old commands
			self.comPort.write("++ifc\n")

			# ensure that connection was successfull
			self.comPort.write("++spoll\n")
			response = self.comPort.readline().strip()
			
			if debug:
				print("Device responded with: '%s'"%(response))

		def getVoltage(self):
			# set device address
			self.comPort.write("++addr %d\n"%(self.addr))
			# request the voltage
			self.comPort.write("VOUT?\n")

			# read until you see the End Or Identify character
			self.comPort.write("++read eoi\n")
			response = self.comPort.readline().strip().split()
			return float(response[1])

		def getCurrent(self):
			# set device address
			self.comPort.write("++addr %d\n"%(self.addr))
			# request the current
			self.comPort.write("IOUT?\n")

			# read until you see the End Or Identify character
			self.comPort.write("++read eoi\n")
			response = self.comPort.readline().strip().split()
			return float(response[1])

		def setVoltage(self,volts):
			# set device address
			self.comPort.write("++addr %d\n"%(self.addr))
			# request the voltage
			self.comPort.write("VSET %f\n"%(volts))

		def setCurrent(self,amperes):
			# set device address
			self.comPort.write("++addr %d\n"%(self.addr))
			# request the current
			self.comPort.write("ISET %f\n"%(amperes))

		def setOutputOn(self,on):
			# set device address
			self.comPort.write("++addr %d\n"%(self.addr))
			if(on):
				self.comPort.write("OUT 1\n")
			else:
				self.comPort.write("OUT 0\n")

		def getOutputOn(self):
			# set device address
			self.comPort.write("++addr %d\n"%(self.addr))
			self.comPort.write("OUT?\n")
			self.comPort.write("++read eoi\n")
			response = self.comPort.readline().strip().split()
			return response[1] == "1"
