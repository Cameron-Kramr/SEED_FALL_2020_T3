import multiprocessing as mp
from enum import Enum
import time
import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
from smbus2 import SMBus

class LCD_CMD(Enum):
	Write = 1
	Message = 2
	CLR_MSSG = 3
	Clear = 4
	Set_Color = 5
	Cursor = 6
	Blink = 7
	Backlight = 8

def LCD_I2C_Handler(input_pipe, size, address, color = [255, 0, 0]):
	i2c_bus = busio.I2C(board.SCL, board.SDA)
	lcd = character_lcd.Character_LCD_RGB_I2C(i2c_bus, size[1], size[0])

	sm_bus = SMBus(1)

	lcd.clear()
	lcd.color = color
	lcd.message("Init LCD Handler Done")

	while(True):
		#Data shape:
		#[cmd, content]
		data = input_pipe.recv()
		print(data)
		#Switch on CMD to decide what to do with content
		if isinstance(data, (list, tuple, np.array)):
			if(data[0] == LCD_CMD.CLR_MSSG):
				lcd.clear()
				lcd.message(str(data[1]))
			elif(data[0] == Clear):
				lcd.clear()
			elif(data[0] == Write):
				lcd.write(int(data[1]))


