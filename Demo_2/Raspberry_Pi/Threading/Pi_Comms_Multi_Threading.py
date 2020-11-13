#Cameron Kramr
#10/09/2020
#EENG 350
#Section A 
#Computer Vision
#NOTE, this module requires pygame to be installed in order to run
#The code in this file deals with communcicating with other devices outside of the raspberry pi.

import multiprocessing as mp
import termios
import os
import sys
from enum import Enum
from enum import IntEnum
import time
import serial
import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
from smbus2 import SMBus
import math
import ctypes

#import spidev

#Create the valid commands for controlling thread operation
class I2C_CMD(IntEnum):
    LCD_CLR_MSG = 1
    SET_CLR = 2

class ARDU_CMD(IntEnum):
    TARGET = 250
    SEND = 1
    RECEIVE = 2

#Main Serial handler thread deals with Serial nonsense.
def Serial_Handler(input_pipe, file = '/dev/ttyACM0', baud = 1000000):
        #Initialize Serial object
    ser = serial.Serial(file, baud)
    FPS = 50
    data2 = ""
    Start = time.time()
    #time.sleep(2)                                                          #might need it so 'ser' can work properly

        #Initialize variables
    data = [0,0,0]

    while (True):
            #Data shape:
        #[command, [magnitude, angle]]

            #Non-blocking read of pipe waiting for input
        try:
            if(input_pipe.poll()):
                data = input_pipe.recv()
            #print("Reading Data")
            while(ser.inWaiting()>0):
                data2 += ser.readline().decode('utf-8')
                #print("Arduino Data:")
                #print(data2)
            #print("Done Reading Data")
            data2 = ""
        except:
            print("Serial Error")

        #print("Looping")
        if(data[0] == ARDU_CMD.SEND):                                         #Clear LCD and send it a string to display
            #try:
            ser.write(bytes(data[1], 'utf-8'))
            print("~~~~~~~~~~~~~~~ Thread Sending Arduino ~~~~~~~~~~~~~~~~")

        data[0] = 0
        #Frame lock arduino
        time.sleep(max(1/FPS - (time.time() - Start),0))

        #time.sleep(time.time() - Start + 1/FPS):


#Main I2C handler thread deals with I2C nonsense.
def I2C_Handler(input_pipe, size, address, color = [0, 255, 0]):
    #Initialize I2C objects
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    lcd = character_lcd.Character_LCD_RGB_I2C(i2c_bus, size[1], size[0])
    lcd.clear()

    #Initialize SMbus object
    sm_bus = SMBus(1)

    #Initialize variables
    I2C_FPS = 10   #Frame rate control for thread to conserve resources
    I2C_Start = 0
    data = [0,0]
    data_in = ctypes.c_int8

    #Initialize LCD screen
    lcd.clear()
    lcd.color = color
    lcd.message = "Init LCD \nHandler Done ;)"

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
        elif(data[0] == I2C_CMD.SET_CLR):
            lcd.color = data[1]
        #Clear data
        data[0] = 0
        #print("Sleep Time: " + str(max(1/I2C_FPS - (time.time() - I2C_Start),0)))
        
        #Frame lock the thread to preserve resources
        time.sleep(max(1/I2C_FPS - (time.time() - I2C_Start),0))
        #print("I2C_FPS: " + str(int(1/(time.time() - I2C_Start))))

if __name__== "__main__":
    Serial_pipe_1, Serial_pipe_2 = mp.Pipe(duplex = True)
    comms = mp.Process(target = Serial_Handler, args=(Serial_pipe_2,))
    comms.start()
    Serial_pipe_1.send([ARDU_CMD.SEND, 123,456])
    Serial_pipe_1.send([ARDU_CMD.SEND, 456,123])
    Serial_pipe_1.send([ARDU_CMD.SEND, 1453,2345])
    Serial_pipe_1.send([ARDU_CMD.RECEIVE, 1453,2345])
    Serial_pipe_1.send([ARDU_CMD.RECEIVE, 1453,2345])
    Serial_pipe_1.send([ARDU_CMD.RECEIVE, 1453,2345])
    Serial_pipe_1.send([ARDU_CMD.RECEIVE, 1453,2345])
    Serial_pipe_1.send([ARDU_CMD.RECEIVE, 1453,2345])
    Serial_pipe_1.send([ARDU_CMD.RECEIVE, 1453,2345])
    choar = input()
    





