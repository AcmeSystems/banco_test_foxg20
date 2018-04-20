#!/usr/bin/python

# flash.py 
# In Circuit Programming utility for FOX Board and Netus G20  

# Versione per banco basato su CM3-Panel

import serial
import time
import sys
import getopt
import string 
from xmodem import XMODEM
import serial
import time
import sys
import getopt
import string 
import datetime
import RPi.GPIO as GPIO

# Comandi VT100
# https://www.csie.ntu.edu.tw/~r92094/c++/VT100.html
color_warning = "\x1B[30;41m" 
color_pass = "\x1B[30;42m" 
color_text = "\x1B[30;43m" 
color_normal = "\x1B[0m" 
clearscreen = "\x1B[2J"
cursorhome = "\x1B[H"

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

GPIO.output(chip_enable,0)
GPIO.output(power_on,0)

elenco_test = {
	"AcmeBoot 1.22":"-",	
	"sda1":"-",
	"sdb1":"-",
	"eth0":"-",
	"login":"-",
	"password":"-",
	"gpio":"-",
}

# Aggiornamento MAC address 
#   filename = nome del file contenente il boot loader

def macUpdate(filename):
	print "Mac update:"

	#If exist a file called macaddress.txt read and increment it
	try:
		f = open("macaddress.txt",'r')
		b = f.read()
		c = "0x" + b[0:2] + b[3:5] + b[6:8] + b[9:11] + b[12:14] + b[15:17]
		d = int(c,16) +1
		a = ("%012X") % d
		b = a[0:2] + ":" + a[2:4]+ ":" + a[4:6] + ":" + a[6:8] + ":" + a[8:10] + ":" + a[10:12]
		f.close()

		f = open("macaddress.txt",'w')
		f.write(b + "\n")
		f.close()
	except:
		print "  Error: macaddress.txt not found"
		exit(1)
	
	#Read the original executable file to send
	f = open(filename,'rb')
	buffer = f.read()
	f.close()

	#Search on it the MagicNumber to know where patch the Mac address
	MacPosition=string.find(buffer, "\x5C\x5C\x5C\x5C") 

	try:
		if MacPosition<>-1:
			MacPosition+=4
			macpatch = chr(int("0x" + a[0:2],16)) + chr(int("0x" + a[2:4],16)) + chr(int("0x" + a[4:6],16)) + chr(int("0x" + a[6:8],16)) + chr(int("0x" + a[8:10],16)) +  chr(int("0x" + a[10:12],16)) 
			patched_bin = buffer[:MacPosition] +  macpatch + buffer[MacPosition+6:]
			f = open(filename + "_patched",'wb')
			f.write(patched_bin)
			f.close()
	except:
		print "  Error: Binary file not patched"
		return

#Define the getc and putc function required from the
#xmodem module
def getc(size, timeout=1):
	data = ser.read(size)
	return data

def putc(data, timeout=1):
	ser.write(data)
	return len(data)

x = XMODEM(getc, putc)

#File contenente il boot loader

filename = "images/acmeboot_dataflash_1.22.bin"
#filename = "images/alexflash.bin"
#filename = "images/acmeboot_dataflash_1.20.bin"
#filename = "images/antiskimmerboot.bin"
#filename = "images/acmeboot_serialflash_1.20.bin"
#filename = "images/acme_boot_dataflash_117.bin"

#Seriale di connessione con la porta di debug della FOX G20
serialdevice = "/dev/ttyS0"

#Open the serial port 
ser = serial.Serial(
	port=serialdevice, 
	baudrate=115200, 
	timeout=1,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS
)  
ser.flushInput()


# Stati di funzionamento:
state=0

def terminal():
	while True:
		s = ser.read(1) 
		sys.stdout.write(s)

token=""	
print "Banco test FOX Board G20"

while True:
	#time.sleep(0.2)

	if state==0:
		print "Lancio programmazione serial flash"

		#Disable the serial flash CE
		GPIO.output(chip_enable,1)

		#Board power-on
		GPIO.output(power_on,1)
		time.sleep(0.2)

		#Enable CE
		GPIO.output(chip_enable,0)
		state=1
		continue

	if state==1:
		print "Lancio programmazione di test"

		#Board power-on
		GPIO.output(power_on,1)
		time.sleep(0.5)

		token=""
		state=2
		continue
			
	if state==2:
		print "In attesa di prompt da RomBOOT"

		ser.flushInput()
		ser.write("#")
		time.sleep(0.2)
		if ser.read(1)=='>':
			state=3
			continue

		#Disable the serial flash CE
		GPIO.output(chip_enable,1)

		#Board power-on
		GPIO.output(power_on,1)
		time.sleep(0.2)

		#Enable CE
		GPIO.output(chip_enable,0)
		state=2
		continue
		
	if state==3:
		print "Trasmissione bootloader"
		
		ser.flushInput()

		address=0x200000
		cmdstring = "S%06X,#" % (address)
		print "  Send: [" + cmdstring + "]"
		ser.write(cmdstring)

		stream = open(filename + "_patched", 'rb')
		x.send(stream)
		stream.close()

		while ser.read(1)!='>':
			time.sleep(0.1)

		macUpdate(filename)

		cmdstring = "G200000#"
		print "  Send: [" + cmdstring + "]"
		ser.write(cmdstring)

		print "  Programmazione serial flash effettuata"

		#terminal()
		
		state=4
		continue

	if state==4:
		s = ser.read(1) 
		sys.stdout.write(s)
		sys.stdout.flush()
		token += s

		pos = token.find("AcmeBoot 1.22")
		if pos >= 0:
			token=""
			elenco_test["AcmeBoot 1.22"]="OK"
			continue
 	
		pos = token.find("sda1")
		if pos >= 0:
			token=""
			elenco_test["sda1"]="OK"
			continue

		pos = token.find("sdb1")
		if pos >= 0:
			token=""
			elenco_test["sdb1"]="OK"
			continue

		pos = token.find("netusg20 login:")
		if pos >= 0:
			token=""
			elenco_test["login"]="OK"
			ser.write("root\r")
			continue

		pos = token.find("Password:")
		if pos >= 0:
			token=""
			elenco_test["password"]="OK"
			ser.write("netusg20\r")
			time.sleep(0.5)
			ser.write("./gpio.py\r")
			continue

		pos = token.find("GPIO test OK")
		if pos >= 0:
			token=""
			dataoracorrente=datetime.datetime.now().strftime("%m%d%H%M%Y")
			comando =  "date " + dataoracorrente + "\r"
			ser.write(comando)

			elenco_test["gpio"]="OK"
			continue

		pos = token.find("200 OK")
		if pos >= 0:
			token=""

			ser.write("halt\r")

			elenco_test["eth0"]="OK"
			continue

		pos = token.find("Power down")
		if pos >= 0:
			token=""
			print "\n"
			print color_text + " Risultato finale dei test" + color_normal
			print "\n"

			for test in elenco_test:
				print "%16s -> " % (test),

				if elenco_test[test]=="OK":
					print color_pass + " OK" + color_normal
				else:
					print color_warning + "error" + color_normal
			
			state=6
			print 
			print "End..."
			
			while True:
				time.sleep(1)
				