#based on 2enum3good.py
'''
Subprocess –
Subprocess is a module in Python that allows us to start new applications or processes in Python.We can use this module to run other programs or execute Linux commands.

'''
import re
import subprocess
device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
df = subprocess.check_output("lsusb")
devices = []
for i in df.split('\n'):
    if i:
        info = device_re.match(i)
        if info:
            dinfo = info.groupdict()
            dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
            devices.append(dinfo)           
for device in devices:
	print(device)


'''
o/p : 
{'device': '/dev/bus/usb/002/002', 'tag': 'Sony Corp. ', 'id': '054c:05ba'}
{'device': '/dev/bus/usb/002/001', 'tag': 'Linux Foundation 2.0 root hub', 'id': '1d6b:0002'}
{'device': '/dev/bus/usb/001/004', 'tag': 'Cambridge Silicon Radio, Ltd Bluetooth Dongle (HCI mode)', 'id': '0a12:0001'}
{'device': '/dev/bus/usb/001/003', 'tag': 'VMware, Inc. Virtual USB Hub', 'id': '0e0f:0002'}
{'device': '/dev/bus/usb/001/002', 'tag': 'VMware, Inc. Virtual Mouse', 'id': '0e0f:0003'}
{'device': '/dev/bus/usb/001/001', 'tag': 'Linux Foundation 1.1 root hub', 'id': '1d6b:0001'}

'''	