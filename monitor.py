#!/usr/bin/python

# monitor.py 
# In Circuit Programming utility for FOX Board and Netus G20  

# Versione per banco basato su CM3-Panel

import serial
import time
import sys
import getopt
import string 
import time
import sys
import getopt
import string 
import datetime
import RPi.GPIO as GPIO
import os

# GPIO usati per inviare comandi
power_on=31
chip_enable=26
switch_up=27
switch_down=28
switch_toggle=29

color_blue = "\x1B[34;40m"
color_white = "\x1B[37;40m"

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 
GPIO.setup(power_on, GPIO.OUT)
GPIO.setup(chip_enable, GPIO.OUT)
GPIO.setup(switch_up, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(switch_down, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(switch_toggle, GPIO.IN,pull_up_down=GPIO.PUD_UP)

GPIO.output(chip_enable,0)
GPIO.output(power_on,0)

print "Monitor"

def startWriting(channel):
	print "Lancia la programmazione"
	os.system("pkill flash.py")
	os.system("pkill toggle_power.py")
	os.system("/home/pi/banco/flash.py <> /dev/console >&0 2>&1 &")

def stopWriting(channel):
	print "Stop programmazione"
	os.system("pkill flash.py")
	os.system("pkill toggle_power.py")
	GPIO.output(chip_enable,0)
	GPIO.output(power_on,0)
	#os.system("clear <> /dev/console >&0 2>&1 &")
	os.system("echo '%s' <> /dev/console >&0 2>&1" % (color_blue + "Alimentazione spenta" + color_white))

def toggle_power(channel):
	print "Premuto"
	os.system("pkill flash.py")
	os.system("pkill toggle_power.py")
	os.system("/home/pi/banco/toggle_power.py <> /dev/console >&0 2>&1 &")
	

GPIO.add_event_detect(switch_up, GPIO.FALLING, callback=startWriting, bouncetime=1000)
GPIO.add_event_detect(switch_down, GPIO.FALLING, callback=stopWriting, bouncetime=1000)
GPIO.add_event_detect(switch_toggle, GPIO.FALLING, callback=toggle_power, bouncetime=1000)

while True:
	time.sleep(1)
	
								