######################################################
#                   DuckHunter                       #
#                 Pedro M. Sosa                      #
# Tool to prevent getting attacked by a rubberducky! #
######################################################

from ctypes import *
import pythoncom
import pyHook 
import win32clipboard
import win32ui
import os
import shutil
from time import gmtime, strftime
from sys import stdout
import imp
duckhunt = imp.load_source('duckhunt', 'duckhunt.conf')

##### NOTES #####
#
# 1. Undestanding Protection Policy:
#   - Paranoid: When an  attack is detected, lock down any further keypresses until the correct password is entered. (set password in .conf file). Attack will also be logged.
#   - Normal :  When an attack is detected, keyboard input will temporarily be disallowed. (After it is deemed that the treat is over, keyboard input will be allowed again). Attack will also be logged.
#   - Sneaky: When an attacks is detected, a few keys will be dropped (enough to break any attack, make it look as if the attacker messed up.) Attack will also be logged.
#   - LogOnly: When an attack is detected, simply log the attack and in no way stop it. 

# 2. How To Use
#   - Modify the user configurable vars below. (particularly policy and password)
#   - Turn the program into a .pyw to run it as windowless script.
#   - (Opt) Use py2exe to build an .exe
#
#################





threshold  = duckhunt.threshold      # Speed Threshold
size       = duckhunt.size           # Size of history array
policy     = duckhunt.policy.lower() # Designate Policy Type
password   = duckhunt.password       # Password used in Paranoid Mode
allow_auto_type_software = duckhunt.allow_auto_type_software #Allow AutoType Software (eg. KeyPass or LastPass)
################################################################################
pcounter   = 0                       # Password Counter (If using password)
speed      = 0                       # Current Average Keystroke Speed
prevTime   = -1                      # Previous Keypress Timestamp
i          = 0                       # History Array Timeslot
intrusion  = False                   # Boolean Flag to be raised in case of intrusion detection
history    = [threshold+1] * size    # Array for keeping track of average speeds across the last n keypresses
randdrop   = duckhunt.randdrop       # How often should one drop a letter (in Sneaky mode)
prevWindow = []                      # What was the previous window
filename   = duckhunt.filename       # Filename to save attacks
blacklist  = duckhunt.blacklist       # Program Blacklist



#Logging the Attack
def log(event):
    global prevWindow

    x = open(filename,"a+")
    if (prevWindow != event.WindowName):
        x.write ("\n[ %s ]\n" % (event.WindowName))
        prevWindow =event.WindowName
    if event.Ascii > 32 and event.Ascii < 127:
        x.write(chr(event.Ascii))
    else:
        x.write("[%s]" % event.Key)
        x.close()
    return


def caught(event):
    global intrusion, policy, randdrop
    print ("Quack! Quack! -- Time to go Duckhunting!")
    intrusion = True;

    
    #Paranoid Policy
    if (policy == "paranoid"):
        win32ui.MessageBox("Someone might be trying to inject keystrokes into your computer.\nPlease check your ports or any strange programs running.\nEnter your Password to unlock keyboard.", "KeyInjection Detected",4096) # MB_SYSTEMMODAL = 4096 -- Always on top.
        return False;
    #Sneaky Policy
    elif (policy == "sneaky"):
        randdrop += 1 
        #Drop every 5th letter
        if (randdrop==7):
            randdrop = 0;
            return False;
        else:
            return True;

    #Logging Only Policy
    elif (policy == "log"):
        log(event)
        return True;


    #Normal Policy
    log(event)
    return False


#This is triggered every time a key is pressed
def KeyStroke(event):

    global threshold, policy, password, pcounter
    global speed, prevTime, i, history, intrusion,blacklist

    print (event.Key);
    print (event.Message);
    print ("Injected",event.Injected);
    
    if (event.Injected != 0 and allow_auto_type_software):
        print ("Injected by Software")
        return True;
    
    
    #If an intrusion was detected and we are password protecting
    #Then lockdown any keystroke and until password is entered
    if (policy == "paranoid" and intrusion):    
        print (event.Key);
        log(event);
        if (password[pcounter] == chr(event.Ascii)):
            pcounter += 1;
            if (pcounter == len(password)):
                win32ui.MessageBox("Correct Password!", "KeyInjection Detected",4096) # MB_SYSTEMMODAL = 4096 -- Always on top.
                intrusion = False
                pcounter = 0
        else:
            pcounter = 0

        return False


    #Initial Condition
    if (prevTime == -1):
        prevTime = event.Time;
        return True


    if (i >= len(history)): i = 0;

    #TypeSpeed = NewKeyTime - OldKeyTime
    history[i] = event.Time - prevTime
    print (event.Time,"-",prevTime,"=",history[i])
    prevTime = event.Time
    speed = sum(history) / float(len(history))
    i=i+1

    print ("\rAverage Speed:",speed)
    
    #Blacklisting    
    for window in blacklist.split(","):
        if window in event.WindowName:
            return caught(event)

    #Intrusion detected
    if (speed < threshold):
        return caught(event)
    else:
        intrusion = False
    # pass execution to next hook registered 
    return True


#################################################################################
#																				#
#                              GUI Using PySimpleGUI							#
#																				#
#################################################################################

import sys
import PySimpleGUI as sg
import subprocess

sg.change_look_and_feel('DarkBlack1')

def callback_function1():
    subprocess.call(['python', 'duckhunt.pyw'], shell=True)
    

def callback_function2():
    subprocess.call(['newfile.log'], shell=True)
 
def callback_function3():
    subprocess.call(['keylog.txt'], shell=True)

def callback_function4():
    subprocess.call(['blacklist.txt'], shell=True)

def callback_function5():
    obj=subprocess.Popen(['python', '3block-unblock.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    sg.popup(obj.stdout.read())


# ------ Column Definition ------ #
column1 = [[sg.Button('      Rescan      ')],
		   [sg.Button('    Event Logs   ')],
		   [sg.Button('Keystroke Logs')],
		   [sg.Button('      Blacklist    ')],
		   [sg.Button(' Block/Unblock ')]]

column2 = [[sg.Text('Device Information', font=("Open Sans ExtraBold",12))],
		   [sg.Text((subprocess.Popen(['python', '1enumeration.py'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)).stdout.read(), size=(42, 7), justification='left', font=("Ariel", 10), relief=sg.RELIEF_RIDGE)]]

layout = [[sg.Text('SAFEPORT', size=(24, 1), justification='center', font=("Vermin Vibes Redux", 42), background_color='orangered', relief=sg.RELIEF_RIDGE)],
		  [sg.Col(column2), 
		  sg.Col(column1)]]


window = sg.Window('Safeport', layout)

while True:                         # Event Loop
    event, values = window.read()
    if event is None:               # if window closed with X
        break
    elif event == '      Rescan      ':
        callback_function1()        # call the "Callback" function
    elif event == '    Event Logs   ':
        callback_function2()        # call the "Callback" function
    elif event == 'Keystroke Logs':
        callback_function3()        # call the "Callback" function
    elif event == '      Blacklist    ':
        callback_function4()        # call the "Callback" function
    elif event == ' Block/Unblock ':
        callback_function5()        # call the "Callback" function


#window.close()

##########################################################################################################


# create and register a hook manager 
kl         = pyHook.HookManager()
kl.KeyDown = KeyStroke

# register the hook and execute forever
kl.HookKeyboard()
pythoncom.PumpMessages()