#!/usr/bin/python

# toggle_power.py 

# Versione per banco basato su CM3-Panel

import os
import time
import RPi.GPIO as GPIO
import serial
import sys

power_on=25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 
GPIO.setup(power_on, GPIO.OUT)

if GPIO.input(power_on)==1:
	GPIO.output(power_on,0)	
	print "toggle_power.py: Power OFF"
else:
	ser = serial.Serial(
		port="/dev/ttyS0", 
		baudrate=115200, 
		timeout=1,
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE,
		bytesize=serial.EIGHTBITS
	)  

	GPIO.output(power_on,1)	
	print "toggle_power.py: Power ON"

	while True:
		c=ser.read(1)
		sys.stdout.write(c)


