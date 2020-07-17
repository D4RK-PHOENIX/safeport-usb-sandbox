print("enter 1 to enable Bluetooth")
print("Enter 0 to disable Bluetooth")
x=input()

if x==0:	
	with open('/etc/udev/rules.d/01-usblockdown.rules', 'w') as f:
		f.write('SUBSYSTEM=="usb", ATTRS{idVendor}=="0a12", ATTRS{idProduct}=="0001", ATTR{authorized}="0"')
else :
	with open('/etc/udev/rules.d/01-usblockdown.rules', 'w') as f:
		f.write('SUBSYSTEM=="usb", ATTRS{idVendor}=="0a12", ATTRS{idProduct}=="0001", ATTR{authorized}="1"')

f=open('/etc/udev/rules.d/01-usblockdown.rules', 'r')
for each in f:
	print(each)