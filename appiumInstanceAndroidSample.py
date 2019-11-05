import time
import socket
import os
import re
import datetime
import sys
import logging
import Queue
import subprocess
import multiprocessing
import errno
socket.setdefaulttimeout(120) #socket time out

from time import sleep
from threading import Thread
from subprocess import Popen, PIPE
from appium import webdriver
 
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

#Update Returned Status from Booleans to Tri-State Strings

#Add Handle For Device Call when device is not connected
#Speed Up Execution. Find VIN in particular
class appiumDeviceAndroid(object):

	def __init__(self, phoneAlias, VIN):
		self.phoneAlias = phoneAlias
		self.commandReceived = ""
		self.vehicleDetailsOrLogAction = False	#When +LOG Flag is set on a command, Use for Vehicle Details or Detailed Log Actions
		self.vehicleControlsAction = False	#When +LOG Flag is set, use for Vehicle Controls Actions
		self.deviceCommandStatus = {"connect" : "Default", "command" : "Default", "close" : "Default"}
		self.actionCommandStatus = ""
		self.errorCode = {"errNum" : 101, "errDescription": "UnableToStartAppiumDeviceErorr", "errLocation" : "appiumInstance.py",
						"screenShot" : "", "paakCommandStatus" : ''}
		self.actionCommandStatus = ""
		self.screenCapturePath = ""
		self.screenCaptureName = ""
		self.StackIdle = { "Idle" : True }
		self.lastBlueToothState = "OFF"
		self.screenShotPath = ''
		self.callAppiumServerTerminalApplication = ""
		self.deviceQueue = multiprocessing.Queue()
		self.deviceThread = Thread(target = self.deviceRunner, args = ())
		if VIN == '':
			self.VIN = ''
		elif VIN == '':
			self.VIN = ''
		else:
			self.VIN = VIN
		
		if (self.phoneAlias == "droidPhone1"):
			#Device Specific Properties (Device Capabilities)
			self.desCapsDevice = {}
			self.desCapsDevice['platformName'] = 'Android'
			self.desCapsDevice['platformVersion'] = '8.0.0'
			self.desCapsDevice['deviceName'] = 'Google Pixel'
			self.desCapsDevice['noReset'] = 'true'
			self.desCapsDevice['appPackage'] = ''
			self.desCapsDevice['appActivity'] = ''
			self.desCapsDevice['autoLaunch'] = 'true'
			self.desCapsDevice['udid'] = ''
			print "New Device Instance ..."
	
	def getApiCommandStatus(self):
		print ("Getting API Command Status ", self.phoneAlias)
		return self.actionCommandStatus

	def getVin(self):
		return self.VIN
	
	def getScreenshotPath(self):
		return self.screenCaptureFolderPath+self.errorCode['screenShot']
	
	def getErrorStatus(self):
		return self.errorCode
	
	def getDeviceStatus(self):	#returns if device is still handing a command, or still connect or still closing
		return self.deviceCommandStatus
		
	def getStackStatus(self):	#returns weather thread is handling or command or not
		return self.StackIdle["Idle"]
	
	def updateStackStatus(self, StackIdleKey):
		self.StackIdle["Idle"] = StackIdleKey
				
	def runThread(self):
		(self.deviceThread).start()

	def appiumCommand(self, someCommand):
		print "Receiving Appium Command "
		self.deviceQueue.put(someCommand)
		print "Appium Command Received " 
			
	def deviceRunner(self):
		print ("In Device Runner Method For: ", self.phoneAlias)
		self.startDeviceAppiumServer()
		try:
			print ("Linking Device Driver to Device, ", self.phoneAlias)
			self.deviceDriver = webdriver.Remote('http://localhost:'+str(self.phonePort)+'/wd/hub',self.desCapsDevice)
			self.errorCode  = {'errNum' : 0, 'errDescription' : "NoError", 'errLocation' : "appiumInstanceAndroid.py", "screenShot" : "", "paakCommandStatus" : ""}
			self.updateDeviceStatus("connect", "Success")
		except:
			raise
			print ("Issue Launching Driver ", self.phoneAlias)
			self.updateDeviceStatus("connect", "Failed")
			#errNum: 102, errDescription: device Driver Error (Check Device Capabilites Matching or Device May not be connected or Appium Server Error)
		
		print ("Server Connect Status, ", self.deviceCommandStatus["connect"])
		while ((self.commandReceived != "EXIT") and (self.deviceCommandStatus["connect"] == 'Success')):
			print ("Awaiting Next Command For ", self.phoneAlias)
			#Get New Command From Queue
			self.commandReceived = (self.deviceQueue.get()).upper()
			print ("Command Received ", self.commandReceived)
			#Set Starting Error Codes For Each Command
			self.errorCode = {"errNum" : 0, "errDescription": "NoError", "errLocation" : "appiumInstance.py", 'screenShot' : '',"paakCommandStatus" : "Default"}
			self.updateDeviceStatus("command", "Default")
			self.actionCommandStatus = "Default"
			
			#screenCapture Details
			thisDay = datetime.datetime.now().strftime("%d-%m-%y")
			thisHourMinuteSecond = datetime.datetime.now().strftime("%H-%M-%S")
			self.screenCaptureFolderPath = os.getcwd()+"/Screenshots/"+self.phoneAlias+"/"+thisDay+"/"+self.commandReceived+"-"+thisHourMinuteSecond+"/"
			self.logCatFilename = ""	#To hold LogCat File Name for the current command
			try:
				os.makedirs(self.screenCaptureFolderPath)
			except os.error as err:
				if (err.errno != errno.EEXIST):
					raise
				pass
				
			sleep(1)
			
			#checkVinFlag = "FAILED" #Used to check if flag is open
			self.updateStackStatus(False) #2, this order is important

			#Is Requested Action A Vehicle Details Action
			try:
				if ((self.commandReceived in self.vehicleDetailsList) or (re.findall('(.+)_',self.commandReceived)[0] in self.vehicleDetailsList)):
					self.vehicleDetailsOrLogAction = True
					print "Capturing Logs After Vehicle Details Command"
			except IndexError:
				print "Command Received Not a Vehicle Details or Detailed-Log Function"
				self.vehicleDetDevcailsOrLogAction = False

			#Is Requested Action A Vehicle Controls Action
			try:
				if ((self.commandReceived in self.vehicleControlsList) or (re.findall('(.+)\+',self.commandReceived)[0] in self.vehicleControlsList)):
					self.vehicleControlsAction = True
					print "Capturing Logs After Vehicle Controls Command"
			except IndexError:
				print "Command Received Not a Vehicle Controls Function"
				self.vehicleControlsAction = False
				self.logoutCommand = False
				self.loginCommand = False

			#Command Branches
			if (self.commandReceived == "EXIT"):
				print "Breaking Out Of Device Command-Handler Loop"
				self.updateDeviceStatus("command", 'Success')
				break
			elif (self.commandReceived == "LOGIN"):
				print ("Handling Device Login ", self.phoneAlias)
				self.errorCode = appiumDeviceLoginAndroid(self.deviceDriver, self.commandReceived, self.phoneAlias, self.screenCaptureFolderPath)
				print ("Return Error Code appiumDeviceLogin ", self.errorCode)
				self.actionCommandStatus = self.errorCode['paakCommandStatus']
				if self.lastBlueToothState == 'ON':
					pass
				else:
					self.errorCode = verifyDeviceBluetoothStatusAndroid(self.deviceDriver, "BLUETOOTHON", self.desCapsDevice['udid'], self.screenCaptureFolderPath)
					if self.errorCode['errNum'] == 0:
						self.lastBlueToothState = "ON"
						print ("lastBlueToothState ", self.lastBlueToothState)
					pass
			elif (self.commandReceived == "LOGOUT"):
				print ("Handling Device Logout ", self.phoneAlias)
				self.errorCode = appiumDeviceLogoutAndroid(self.deviceDriver, self.phoneAlias, self.screenCaptureFolderPath)
			elif(self.commandReceived == "BLUETOOTHOFF"):
				print ("Handling Device BLUETOOTHOFF ", self.phoneAlias)
				if self.lastBlueToothState == "OFF":
					#bluetooth Already OFF
					print ("bluetooth Already Off For ", self.phoneAlias)
					self.errorCode["errNum"] = 0
					self.errorCode["errDescription"] = "NoError"
					self.errorCode["errLocation"] = "appiumInstanceIOS.py"
					btStatusfile_name = self.screenShotPath+"BLUETOOTHOFF"+".png"
					self.deviceDriverIOS.save_screenshot(btStatusfile_name)
					self.errorCode['screenShot'] = btStatusfile_name
					self.actionCommandStatus = "Success"
				elif self.lastBlueToothState == "ON":
					self.errorCode = verifyDeviceBluetoothStatus(self.deviceDriver, "BLUETOOTHOFF", self.desCapsDevice['udid'], self.screenCaptureFolderPath)
					if self.errorCode["errNum"] == 0:
						print "Assing lastBlueToothState State Off"
						self.lastBlueToothState = "OFF"
						self.actionCommandStatus = self.errorCode['paakCommandStatus']
			elif(self.commandReceived == "BLUETOOTHON"):
				print ("Handling Device BLUETOOTHON ", self.phoneAlias)
				print ("Last lastBlueToothState ", self.lastBlueToothState)
				if self.lastBlueToothState == "ON":
					#bluetooth Already ON
					print ("bluetooth Already On For ", self.phoneAlias)
					self.errorCode["errNum"] = 0
					self.errorCode["errDescription"] = "NoError"
					self.errorCode["errLocation"] = "appiumInstanceIOS.py"
					btStatusfile_name = self.screenShotPath+"BLUETOOTHON"+".png"
					self.deviceDriverIOS.save_screenshot(btStatusfile_name)
					self.errorCode['screenShot'] = btStatusfile_name
				elif self.lastBlueToothState == "OFF":	
					self.errorCode = verifyDeviceBluetoothStatus(self.deviceDriver, "BLUETOOTHON", self.desCapsDevice['udid'], self.screenCaptureFolderPath)
					if self.errorCode["errNum"] == 0:
						self.lastBlueToothState = "ON"
					pass
			else:
				print ("Unrecognized Command {0}, for {1}".format(self.commandReceived, self.phoneAlias))
				self.errorCode = {"errNum" : 115, "errDescription": "Unrecognized Appium Command", "errLocation" : "appiumInstance.py", 'screenShot' : os.getcwd()+'UnrecognizedCommandError.png','paakCommandStatus' : 'Failed'}
			self.vehicleControlsAction = False
			self.logoutCommand = False
			self.loginCommand = False
			self.vehicleDetailsOrLogAction = False
			self.updateDeviceStatus("command", "Success")	#1
			self.updateStackStatus(True) #2, this order is important, these values are use by appiumCommand to timeout command
			sleep(1)	#Check For New Item Every Second
		print ("Outside While Loop")
		if (self.deviceCommandStatus['connect'] == 'Failed'):
			self.errorCode  = {'errNum' : 101, 'errDescription' : "UnableToStartAppiumDeviceErorr", 'errLocation' : "appiumInstanceIOS.py", "screenShot" : os.getcwd()+'ServerConnectError.png', "paakCommandStatus" : "Failed"}
			self.actionCommandStatus = "Failed"
		#Error Code if connect fails
		self.killDeviceInstance()
		self.killAppiumServer()	
	
	def launchServer(self):
		print ("Launching Appium Server ", self.phoneAlias)
		serverRunning = False
		loopUntilServerIsRunning = 30
		#Launch Appium Server, Opens up Appium Server instance in the background. 
		osCommand = "open -a Terminal "+self.callAppiumServerTerminalApplication
		os.system(osCommand)
		while loopUntilServerIsRunning > 0:	#Wait up to 30 seconds for server to run
			loopUntilServerIsRunning -= 1
			print loopUntilServerIsRunning
			sleep(1)
			checkPortOutput = Popen('netstat -vanp tcp | grep '+self.phonePort , shell=True, stdout=PIPE).stdout
			output = checkPortOutput.read()
			if output: #Check if Server is running after Launch
				print "Breaking Out of Listenning While Loop"
				serverRunning = True
				break
		#errNum: 101, errDescription: Appium Server Starting  Error
	
	def startDeviceAppiumServer(self):
		print ("Starting Device ", self.phoneAlias)
		if (self.phoneAlias == "droidPhone1"):
			self.phonePort = "4723" 			#Assign Real Device an Appium Server
			self.callAppiumServerTerminalApplication = "./appiumPort"+self.phonePort+".sh"		#Assign Device Appium Server Shell Script Name
		elif(self.phoneAlias == "droidPhone2"):
			self.phonePort = "4725"				#Assign Real Device an Appium Server
			self.callAppiumServerTerminalApplication = "./appiumPort"+self.phonePort+".sh"
		elif(self.phoneAlias == "droidPhone3"):
			self.phonePort = "4727"				#Assign Real Device an Appium Server
			self.callAppiumServerTerminalApplication = "./appiumPort"+self.phonePort+".sh"
		elif(self.phoneAlias == "droidPhone4"):
			self.phonePort = "4729"				#Assign Real Device an Appium Server
			self.callAppiumServerTerminalApplication = "./appiumPort"+self.phonePort+".sh"
		elif(self.phoneAlias == "droidPhone5"):
			self.phonePort = "4731"				#Assign Real Device an Appium Server
			self.callAppiumServerTerminalApplication = "./appiumPort"+self.phonePort+".sh"

		terminalOutput = Popen('netstat -vanp tcp | grep '+self.phonePort , shell=True, stdout=PIPE).stdout 	#Check If Server Not already running
		output = terminalOutput.read()
		if not output:		#Server Not running. Launch Server but Server might be in TimeWait)
			self.launchServer()
		else:
			if re.search("TIME_WAIT", output):
				print ('Appium Server At Port {0} is in TIME_WAIT state'.format(self.phonePort))
				#Wait until timeWaitMaxSeconds for server to exit TIME_WAIT
				timeWaitMaxSeconds = 45 # Max sleep time, in seconds
				while timeWaitMaxSeconds > 0:
					timeWaitMaxSeconds-=1
					sleep(1)
					terminalOutput = Popen('netstat -vanp tcp | grep '+self.phonePort , shell=True, stdout=PIPE).stdout 	#Check Server Status
					output = terminalOutput.read()
					print ("Max Seconds Appium Server Port Still in TIME_WAIT - {0}".format(timeWaitMaxSeconds))
					if not output:
						print ("Server No longer in TIME_WAIT".format(self.phonePort))
						break
				self.launchServer()
			else:
				print ("Server on {0} is already running".format(self.phonePort))
			
	
	def killAppiumServer(self):
		terminalOutput = Popen('netstat -vanp tcp | grep '+self.phonePort , shell=True, stdout=PIPE).stdout
		output = terminalOutput.read()
		portProcessPID = re.findall('[A-Z]+\s+[0-9]+\s+[0-9]+\s+([0-9]+)', output)
		if portProcessPID:
			for eachPID in portProcessPID:
				print ("Killing Server On Port {0} and PID {1}".format(self.phonePort, eachPID))
				os.system("kill -9 "+eachPID)
				thisHourMinuteSecond = datetime.datetime.now().strftime("%H-%M-%S")
				print ("Before Server Kill ", thisHourMinuteSecond)
			waitWhileTime_Wait = 60
			while waitWhileTime_Wait > 0:
				waitWhileTime_Wait -= 1
				sleep(1)
				checkPortOutput = Popen("netstat -vanp tcp | grep "+self.phonePort, shell = True, stdout = PIPE).stdout
				output = checkPortOutput.read()
				if not output:
					print "Appium Server No Longer In TIME_WAIT State , Server Closed"
					print ("Port Output After Server Kill ", output)
					break
		else:
			print ("Server On Port {0} Is Not Running".format(self.phonePort))
			
	def killDeviceInstance(self):
		print "Killing Device Instance ..."
		self.deviceDriver.quit()
		self.updateDeviceStatus("close", "Success")

if __name__ == '__main__':
	phoneID = 'droidPhone2'
	vin = '2LMPJ8LR8HBL44142'
	droidDeviceInstance = appiumDeviceAndroid(phoneID, vin)
	droidDeviceInstance.runThread()
	droidDeviceInstance.appiumCommand("LOGIN")
	droidDeviceInstance.appiumCommand("LOGOUT")
	droidDeviceInstance.appiumCommand('EXIT')
		
		
