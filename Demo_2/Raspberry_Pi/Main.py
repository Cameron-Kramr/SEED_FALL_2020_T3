#Cameron Kramr
#11/06/2020
#EENG 350
#Section A
#Computer Vision
#NOTE, this module requires pygame to be installed in order to run
#This file ties together all the project files and implements the program structure

#System Imports
import sys
import numpy as np
import time
import math

#Custom Library Imports
#import Detection.detect_angle as dta
import Robot

#import Modules.GPS_Handler



robot = Robot.Demo_2_Robot()
#robot.Debug = True

robot.start_All_Threads()

robot.debug_All_Modules()

while(True):
    robot.update_Modules()
