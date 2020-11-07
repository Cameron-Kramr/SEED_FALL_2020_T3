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
class I2C_CMD(Enum):
    LCD_CLR_MSG = 1
    WRITE_ARDU = 2
    FETCH_ANGLE = 3

class ARDU_CMD(IntEnum):
    TARGET = 250
    SEND = 1
    RECEIVE = 2

#Main Serial handler thread deals with Serial nonsense.
def Serial_Handler(input_pipe, file = '/dev/ttyACM0', baud = 250000):
        #Initialize Serial object
    ser = serial.Serial(file, baud)
    FPS = 100
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

            while(ser.inWaiting()>0):
                data2 += ser.readline().decode('utf-8')
                #print("Arduino Data:")
                #print(data2)
        except:
            print("Serial Error")

        #print("Looping")
        if(data[0] == ARDU_CMD.SEND):                                         #Clear LCD and send it a string to display
            try:
            #ser.write((' '.join([str(item) for item in data[1]]
                for i in data[1]:
                    if(i != '\n'):
                        ser.write(i.encode())
                        #print(i)
                #print("Sent Ardu:" + str(data[1]))
                    #pass
            except:
                print("Something's wrong with sending Serial Data!")

        if(data2 != ""):                                      #if we need to get the position from arduino, this if statement
                                                                            #will do it. Feel free to alter "get_position" to whatever you want.
            try:
                #data2 = ser.readline().decode('utf-8').rstrip()                 #gets data from arduino
                input_pipe.send(data2)
                data2 = ""
                pass
            except:
                print("Something's wrong with getting Serial Data!")
        #Clear data
        data[0] = 0
        #Frame lock arduino
        while(time.time() - Start < 1/FPS):
            pass


#Main I2C handler thread deals with I2C nonsense.
def I2C_Handler(input_pipe, size, address, color = [255, 0, 0]):
    #Initialize I2C objects
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    lcd = character_lcd.Character_LCD_RGB_I2C(i2c_bus, size[1], size[0])
    lcd.clear()

    #Initialize SMbus object
    sm_bus = SMBus(1)

    #Initialize variables
    I2C_FPS = 100   #Frame rate control for thread to conserve resources
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
        elif(data[0] == I2C_CMD.WRITE_ARDU): #Write to the arduino                                          #not needed anymore?
            try:
                print(data[1])
                sm_bus.write_byte_data(address, 0, int(data[1]))
            except:
                print("SM Bus Error!")
                sm_bus = SMBus(1)
        elif(data[0] == I2C_CMD.FETCH_ANGLE): #Fetch the angle from the arduino                             #not needed anymore?
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
    





