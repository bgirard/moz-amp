#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys
import serial
import time

# when we run from Notepad++, the working directory is wrong - fix it here
currentPath = os.path.dirname(os.path.abspath(__file__))
os.chdir(currentPath)

from Tkinter import *


def ProcessPacket(packetBytes):
	packetLength = len(packetBytes)
#	if packetLength != 86:
#		print 'Packet is not 86 bytes long - {} bytes'.format(packetLength)
#		return

	global PacketCount
	global CurrentTotal
	global MinCurrent
	global MaxCurrent

	dataPortion = packetBytes[5:packetLength-1]
	dataCount = len(dataPortion) / 8
	for index in range(0, dataCount):
		startIndex = index * 8
		endIndex = startIndex + 8
		sampleBytes = dataPortion[startIndex:endIndex]
		current = ord(sampleBytes[0]) + (ord(sampleBytes[1]) * 256)
		if (current > 32767):
			current = (65536 - current) * -1;
		voltage = ord(sampleBytes[2]) + (ord(sampleBytes[3]) * 256)
		msCounter = ord(sampleBytes[4]) + (ord(sampleBytes[5]) * 256) + (ord(sampleBytes[6]) * 65536) + (ord(sampleBytes[7]) * 16777216)
		print 'Sample %(index)d  - current: %(current)d voltage: %(voltage)d msCounter: %(counter)d' \
			% {"index": index, "current": current, "voltage": voltage, "counter": msCounter}
		PacketCount = PacketCount + 1
		CurrentTotal = CurrentTotal + current
		if current < MinCurrent:
			MinCurrent = current
		if current > MaxCurrent:
			MaxCurrent = current

def ProcessPacketFromSerial(serialPort):
	header = ord(serialPort.read(1))
	if header != 255:
		print 'Header is not 255: {}'.format(header)
		return
	header = ord(serialPort.read(1))
	if header != 255:
		print 'Header is not 255: {}'.format(header)
		return
	boardId = ord(serialPort.read(1))
	if boardId != 1:
		print 'Board ID is not 1: {}'.format(boardId)
		return
	packetLength = ord(serialPort.read(1))
#	if packetLength != 82:
#		print 'Packet length is not 82, instead it is {}'.format(packetLength)
#		return
	command = ord(serialPort.read(1))
	if command != 4:
		print 'Command is not PACKET_CMD_ASYNC: {}'.format(command)
		return
	dataPortion = serialPort.read(packetLength - 2)
	dataCount = len(dataPortion) / 8
	for index in range(0, dataCount):
		startIndex = index * 8
		endIndex = startIndex + 8
		sampleBytes = dataPortion[startIndex:endIndex]
		current = ord(sampleBytes[0]) + (ord(sampleBytes[1]) * 256)
		if (current > 32767):
			current = (65536 - current) * -1;
		voltage = ord(sampleBytes[2]) + (ord(sampleBytes[3]) * 256)
		msCounter = ord(sampleBytes[4]) + (ord(sampleBytes[5]) * 256) + (ord(sampleBytes[6]) * 65536) + (ord(sampleBytes[7]) * 16777216)
		print 'Sample %(index)d  - current: %(current)d voltage: %(voltage)d msCounter: %(counter)d' \
			% {"index": index, "current": current, "voltage": voltage, "counter": msCounter}
		crc = ord(serialPort.read(1))


print 'MozAmpTest'

# serialPort = serial.Serial(port='/dev/ttyACM0', baudrate=1000000, timeout=1)
serialPort = serial.Serial(port='COM7', baudrate=1000000, timeout=1)

# commandBytes = bytearray.fromhex("ff ff 01 02 01 FB") #SET_ID
# commandBytes = bytearray.fromhex("ff ff 01 02 02 FA") #START_ASYNC
# commandBytes = bytearray.fromhex("ff ff 01 02 03 F9") #STOP_ASYNC
# commandBytes = bytearray.fromhex("ff ff 01 02 05 F7") #TURN_OFF_BATTERY
# commandBytes = bytearray.fromhex("ff ff 01 02 06 F6") #TURN_ON_BATTERY
commandBytes = bytearray.fromhex("ff ff 01 02 07 F5") #SEND_SAMPLE

serialPort.flushInput()

PacketCount = 0
CurrentTotal = 0
MinCurrent = 65536
MaxCurrent = -65536

for index in range(0, 100):
	serialPort.write(commandBytes)
	serialPort.flush()
	bytes = serialPort.read(14)
	ProcessPacket(bytes)

average = CurrentTotal / PacketCount
print ''
print 'Average: %(average)d' % {"average": average}
print 'Min:     %(min)d' % {"min": MinCurrent}
print 'Max:     %(max)d' % {"max": MaxCurrent}


#f = open('data.txt', 'wb')
#f.write(bytes)
#f.close()


# ProcessPacketFromSerial(serialPort)

#commandBytes = bytearray.fromhex("ff ff 01 02 03 F9") #STOP_ASYNC
#serialPort.write(commandBytes)
#serialPort.flush()

count = serialPort.inWaiting()
if count > 0:
	print 'Flushing {} bytes'.format(count)
	junk = serialPort.read(count)
serialPort.flushInput()
serialPort.close()
