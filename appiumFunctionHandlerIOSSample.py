import os
import re
import subprocess
import multiprocessing
import datetime

from selenium.common.exceptions import InvalidSelectorException, NoSuchElementException

from appium import webdriver
from time import sleep
from threading import Thread
from subprocess import PIPE, Popen


def vehicleControlsDictionary (actionCode):
	return {
		"VEHICLE-STATUS" : "Vehicle Status",
		"LOCKS" : "Locks",
		"START" : "Start",
		"LIFTGATE" : "Liftgate",
		"UNLOCK-DRIVER-DOOR" : "Unlock Driver Door",
		"UNLOCK-ALL-DOORS" : "Unlock All Doors",
		"UNLOCK-CARGO-DOOR" : "Unlock Cargo Door",
		"UNLOCK-ALL-DOORS-PLUS-CARGO-DOOR" : "Unlock All Doors Plus Cargo Door",
		"LOCK-ALL" : "Lock All",
		"DOUBLE-LOCK" : "Double Lock",
		"DECK-LID-RELEASE" : "Deck Lid Release",
		"LIFT-GATE-RELEASE" : "Lift Gate Release",
		"LIFT-GATE-GLASS-RELEASE" : "Lift Gate Glass Release",
		"GLOBAL-OPEN" : "Global Open",
		"GLOBAL-CLOSE" : "Global Close",
		"POWER-LIFT-GATE" : "Power Lift Gate",
		"LEFT-POWER-SLIDING-DOOR" : "Left Power Sliding Door",
		"RIGHT-POWER-SLIDING-DOOR" : "Right Power Sliding Door",
		"POWER-DECK-LID" : "Power Deck Lid",
		"REMOTE-START" : "Remote Start",
		"REMOTE-STOP" : "Remote Stop",
		"ENGAGE-PANIC" : "Engage Panic",
		"STOP-PANIC" : "Stop Panic",
		}[actionCode]

def verifyDeviceBluetoothStatusIOS(adlDeviceDriverIOSBluetooth, bluetoothRequest, deviceUdid, adlScreenCaptureFolderPath):
	bTBundleId = {'bundleId' : 'com.apple.Preferences'}
	doCommand = bluetoothRequest
	screenShot = doCommand+".png"
	errorCode = {"errNum" : 0, "errDescription" : "NoError",
	 "errLocation" : "verifyDeviceBluetoothStatusIOS-appiumFunctionHandler.py", "screenShot" : screenShot}
	isScreenSettings = False
	isScreenBT = False

	isScreenBT = verifyScreen(adlDeviceDriverIOSBluetooth, "bluetoothSettings")
	if not isScreenBT:
		isScreenSettings = verifyScreen(adlDeviceDriverIOSBluetooth, "Settings")
		if isScreenSettings: 
			pass
		else:
			try: 
				adlDeviceDriverIOSBluetooth.launch_app()
				print "Launched Settings Successfully"
			except:
				print "Issues Launching Settings"
				errorCode["errNum"] = 106
				errorCode["errDescription"] = "Unable to Launch Bluetooth or Settings App"
				file_name = adlScreenCaptureFolderPath+doCommand+"LaunchBluetoothError"+".png"
				adlDeviceDriverIOSBluetooth.save_screenshot(file_name)
				errorCode['screenShot'] = file_name

		sleep(1)
		isScreenSettings = verifyScreen(adlDeviceDriverIOSBluetooth, "Settings")
		if isScreenSettings:
			print "Settings Screen Launched Successfully "
			try:
				btElementSettings = adlDeviceDriverIOSBluetooth.find_element_by_id(u'Bluetooth')
				btElementSettings.click()
				sleep(1)
			except NoSuchElementException:
				errorCode["errNum"] = 115
				errorCode["errDescription"] = "No Such Elemnent "
				file_name = adlScreenCaptureFolderPath+doCommand+"NoSuchElementError"+".png"
				adlDeviceDriverIOSBluetooth.save_screenshot(file_name)
				errorCode['screenShot'] = file_name
		else: 
			print "Settings Screen Launch Failed"

		isScreenBT = verifyScreen(adlDeviceDriverIOSBluetooth, "bluetoothSettings")
		if isScreenBT:
			print "Bluetooth SUccess "
		else: 
			print "No Success Bluetooth"

	if isScreenBT:
		sleep(1)
		btTextViewElements = adlDeviceDriverIOSBluetooth.find_elements_by_class_name('XCUIElementTypeTextView')
		if bluetoothRequest == "BLUETOOTHON":
			if btTextViewElements:
				print ("Bluetooth Already ON ")
				for eachElement in btTextViewElements:
					print ("btTextViewElements ", eachElement.text)
			else:
				try:
					print "Turning On Bluetooth"
					btSwitchElements = adlDeviceDriverIOSBluetooth.find_elements_by_class_name('XCUIElementTypeSwitch')
					for eachElement in btSwitchElements:
						eachElement.click()
						print "Turned Bluetooth On"
					sleep(2)
					btTextViewElements = adlDeviceDriverIOSBluetooth.find_elements_by_class_name('XCUIElementTypeTextView')
					if btTextViewElements:
						print "Bluetooth Successfully Turned On"
						errorCode["errNum"] = 0
						errorCode["errDescription"] = "NoError"
						file_name = adlScreenCaptureFolderPath+doCommand+".png"
						adlDeviceDriverIOSBluetooth.save_screenshot(file_name)
						errorCode['screenShot'] = file_name
				except:
					print "Issue turning on BT, verifyDeviceBluetoothStatusIOS-appiumFunctionHandler"
					errorCode["errNum"] = 104
					errorCode["errDescription"] = "Unable To Call Driver Driver"
					file_name = adlScreenCaptureFolderPath+doCommand+"DeviceDriverError"+".png"
					adlDeviceDriverIOSBluetooth.save_screenshot(file_name)
					errorCode['screenShot'] = file_name
		elif bluetoothRequest == "BLUETOOTHOFF":
			btTextViewElements = adlDeviceDriverIOSBluetooth.find_elements_by_class_name('XCUIElementTypeTextView')
			if not btTextViewElements:
				print "Bluetooth is Already turned off"
			else:
				for eachElement in btTextViewElements:
					print ("btTextViewElements ", eachElement.text)
				try:
					btSwitchElements = adlDeviceDriverIOSBluetooth.find_elements_by_class_name('XCUIElementTypeSwitch')
					for eachElement in btSwitchElements:
						eachElement.click()
						print "Turning OFF Bluetooth"
					sleep(2)
					btTextViewElements = adlDeviceDriverIOSBluetooth.find_elements_by_class_name('XCUIElementTypeTextView')
					if btTextViewElements:
						print "Bluetooth Successfully Turned OFF"
						errorCode["errNum"] = 0
						errorCode["errDescription"] = "NoError"
						file_name = adlScreenCaptureFolderPath+doCommand+".png"
						adlDeviceDriverIOSBluetooth.save_screenshot(file_name)
						errorCode['screenShot'] = file_name
				except:
					print "Issue turning OFF BT, verifyDeviceBluetoothStatusIOS-appiumFunctionHandler"
					errorCode["errNum"] = 104
					errorCode["errDescription"] = "Unable To Call Driver Driver"
					file_name = adlScreenCaptureFolderPath+doCommand+"DeviceDriverError"+".png"
					adlDeviceDriverIOSBluetooth.save_screenshot(file_name)
					errorCode['screenShot'] = file_name
					#adlDeviceDriverIOSBluetooth.save_screenshot(adlScreenCaptureFolderPath+file_name)

	else:
		print "Unable to Launch Bluetooth Settings Screen"
		errorCode["errNum"] = 106
		errorCode["errDescription"] = "Unable to Launch Bluetooth App"
		file_name = adlScreenCaptureFolderPath+doCommand+"LaunchBluetoothError"+".png"
		adlDeviceDriverIOSBluetooth.save_screenshot(file_name)
		errorCode['screenShot'] = file_name

		#adlDeviceDriverIOSBluetooth.save_screenshot(adlScreenCaptureFolderPath+file_name)

	return errorCode





