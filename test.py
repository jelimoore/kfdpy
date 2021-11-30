import kfdpy
import logging
import time

logging.basicConfig(format='%(asctime)-15s %(levelname)s:%(module)s:    %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)


kfd = kfdpy.KFDTool('COM9')

print("Adapter version: {}".format(kfd.getAdapterVer()))
print("Firmware Version: {}".format(kfd.getFwVer()))
print("UID: {}".format(kfd.getUID()))
print("Model: {}".format(kfd.getModel()))
print("Hardware Version: {}".format(kfd.getHwRev()))
print("Serial Number: {}".format(kfd.getSerialNumber()))

time.sleep(5)
#print(kfd.selfTest())

result = kfd.detectRadio()

print ("Detect radio result: {}".format(result))

kfd.close()

