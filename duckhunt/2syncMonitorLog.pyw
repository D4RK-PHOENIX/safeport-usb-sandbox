#sync monitor
from __future__ import print_function
import pyudev

#importing module 
import logging 
logging.basicConfig(filename="newfile.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='a') 
  
#Creating an object 
logger=logging.getLogger() 
#Setting the threshold of logger to DEBUG 
logger.setLevel(logging.DEBUG) 

#print('Press Ctrl+x to come out of loop')
context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by('block')
for device in iter(monitor.poll, None):
		if 'ID_FS_TYPE' in device:
			#print('{0} partition {1}'.format(device.action, device.get('ID_FS_LABEL')))
			temp=('{0} partition {1}'.format(device.action, device.get('ID_FS_LABEL')))
			logger.info(temp)
			print(temp)
print("over and out")

'''
o/p : 
remove partition PARROT_OS
remove partition None
add partition None
also store into log file "newfile.log"
'''