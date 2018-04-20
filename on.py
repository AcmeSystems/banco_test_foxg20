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
power_on=25
chip_enable=26
switch_up=27
switch_down=28
home_state=29

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 
GPIO.setup(power_on, GPIO.OUT)
GPIO.setup(chip_enable, GPIO.OUT)
GPIO.setup(switch_up, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(switch_down, GPIO.IN,pull_up_down=GPIO.PUD_UP)

GPIO.output(chip_enable,0)
GPIO.output(power_on,1)	
								