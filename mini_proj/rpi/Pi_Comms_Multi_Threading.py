#Cameron Kramr
#10/09/2020
#EENG 350
#Section A 
#Computer Vision
#NOTE, this module requires pygame to be installed in order to run
#The code in this file deals with communcicating with other devices outside of the raspberry pi.

import multiprocessing as mp
from enum import Enum
from enum import IntEnum
import time
import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
from smbus2 import SMBus
import math
import ctypes

#import spidev

#Create the valid commands for controlling thread operation
class I2C_CMD(Enum):
	LCD_CLR_MSG = 1
	WRITE_ARDU = 2
	FETCH_ANGLE = 3

class ARDU_CMD(IntEnum):
	TARGET = 250

#Main I2C handler thread deals with I2C nonsense.
def I2C_Handler(input_pipe, size, address, color = [255, 0, 0]):
	#Initialize I2C objects
	i2c_bus = busio.I2C(board.SCL, board.SDA)
	lcd = character_lcd.Character_LCD_RGB_I2C(i2c_bus, size[1], size[0])
	lcd.clear()
	
	#Initialize SMbus object
	sm_bus = SMBus(1)

	#Initialize variables
	I2C_FPS = 100	#Frame rate control for thread to conserve resources
	I2C_Start = 0
	data = [0,0]
	data_in = ctypes.c_int8

	#Initialize LCD screen
	lcd.clear()
	lcd.color = color
	lcd.message = "Init LCD Handler Done"

	while(True):
		#Record time
		I2C_Start = time.time()
		#Data shape:
		#[cmd, content]
		
		#Non-blocking read of pipe waiting for input
		if(input_pipe.poll()):
			data = input_pipe.recv()
		#Switch on command portion of data to figure out what to do
		if(data[0] == I2C_CMD.LCD_CLR_MSG): #Clear LCD and send it a string to display
			try:
				#time.sleep(0.1)
				lcd.clear()
				lcd.message = str(data[1])
				pass
			except:
				print("SM Bus Error!")
		elif(data[0] == I2C_CMD.WRITE_ARDU): #Write to the arduino
			try:
				print(data[1])
				sm_bus.write_byte_data(address, 0, int(data[1]))
			except:
				print("SM Bus Error!")
				sm_bus = SMBus(1)
		elif(data[0] == I2C_CMD.FETCH_ANGLE): #Fetch the angle from the arduino
			#print(sm_bus.read_byte_data(address, 0))
			try:
				#Need to preserve the sign to make this sensible, use ctypes for that
				data_in = ctypes.c_int8(sm_bus.read_byte_data(address, 0))
				#Convert data in from byte to degree angle
				data_in = data_in.value/128*180
				
				#Send angle down pipe
				input_pipe.send(data_in)
			except:
				print("SM Bus Error!")
		#Clear data
		data[0] = 0
		#print("Sleep Time: " + str(max(1/I2C_FPS - (time.time() - I2C_Start),0)))
		
		#Frame lock the thread to preserve resources
		time.sleep(max(1/I2C_FPS - (time.time() - I2C_Start),0))
		#print("I2C_FPS: " + str(int(1/(time.time() - I2C_Start))))


'''
def ARD_SPI_Handler(input_pipe, address, speed, mode, ):
	FPS = 10
	start_time = 0

	data = board .MOSI
	latch = board.D5

	spi_bus = spidev.SpiDev()
	spi.open(0,0)
	spi.mode = ob11


	while(True):
		#Data shape:
		#[content]
		if(input_pipe.poll()):
			data = input_pipe.recv()
		#Send data to arduino 
			SEND_SPI_DATA_2_ARDUINO(data)

		#If data from Arduino available, send it down the pipe
		if(SPI_ARDU_DATA):
			data = SPI_ARDU_DATA_GET()
			input_pip.send(data)

		#Wait until time to go
		while(start_time - time.time() < 1/FPS):


'''
