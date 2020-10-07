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

class I2C_CMD(Enum):
	LCD_CLR_MSG = 1
	WRITE_ARDU = 2
	FETCH_ANGLE = 3

class ARDU_CMD(IntEnum):
	TARGET = 250

def I2C_Handler(input_pipe, size, address, color = [255, 0, 0]):
	i2c_bus = busio.I2C(board.SCL, board.SDA)
	lcd = character_lcd.Character_LCD_RGB_I2C(i2c_bus, size[1], size[0])
	lcd.clear()
	sm_bus = SMBus(1)

	I2C_FPS = 100
	I2C_Start = 0
	data = [0,0]
	data_in = ctypes.c_int8

	lcd.clear()
	lcd.color = color
	lcd.message = "Init LCD Handler Done"

	while(True):
		I2C_Start = time.time()
		#Data shape:
		#[cmd, content]
		if(input_pipe.poll()):
			data = input_pipe.recv()

		if(data[0] == I2C_CMD.LCD_CLR_MSG):
			try:
				#time.sleep(0.1)
				#lcd.clear()
				#lcd.message = str(data[1])
				pass
			except:
				print("SM Bus Error!")
		elif(data[0] == I2C_CMD.WRITE_ARDU):
			#sm_bus.write_byte_data(address, 0, (ARDU_CMD.TARGET))
			try:
				print(data[1])
				sm_bus.write_byte_data(address, 0, int(data[1]))
			except:
				print("SM Bus Error!")
				sm_bus = SMBus(1)
		elif(data[0] == I2C_CMD.FETCH_ANGLE):
			#print(sm_bus.read_byte_data(address, 0))
			try:
				data_in = ctypes.c_int8(sm_bus.read_byte_data(address, 0))
				data_in = data_in.value/128*180
				#print(str(int(data_in.value)))
				input_pipe.send(data_in)
			except:
				print("SM Bus Error!")
		data[0] = 0
		#print("Sleep Time: " + str(max(1/I2C_FPS - (time.time() - I2C_Start),0)))
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
