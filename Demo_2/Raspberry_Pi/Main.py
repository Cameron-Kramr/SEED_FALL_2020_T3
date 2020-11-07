#Cameron Kramr
#10/09/2020
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
import Detection.detect_angle as dta
import Robot.py


#Main Variables:
FPS = 60
start_time = 0
LCD_FPS = 0.7
LCD_Start_Time = 0
angle_in = 0
LCD_OUTPUT = False
rotations = [0,0,0]
Ardu_FPS = 60
Ardu_Start = 0
terminal_msg = None
compound = False
compound_time = 15
compound_start = 0

#Main Running Loop
while(True):

    #While pose thread yields translation and rotation information, process it
    while(cv2_conn1.poll()):

        #Collect the poses
        poses = cv2_conn1.recv()

        #Create the correct rotation matrix from condensed form of the first detected marker
        rot_mtx, jacob = cv2.Rodrigues(poses[0][1][0][0])

        #Find rotation from expanded rotation matrix
        rotations = dta.calc_Euclid_Angle(rot_mtx) * 180/math.pi

        angle = math.atan2(poses[0][2][0][0][2], poses[0][2][0][0][0])*180/math.pi - 90
        print(angle)
        Message = "ID: " + str(poses[0][0][0]) + "\nX: " + str(angle)



    #Store any terminal information
    terminal_msg = pcmt.Get_Line()

    if(terminal_msg != None):
        #print(terminal_msg[-2])
        #print("checking compounding")
        if(terminal_msg[-2] == 'c'):
            print("initiating compound movement")
            compound = True
            compound_start = time.time()
        if(27 in terminal_msg):
            break

    #Lock FPS to not waste resources
    end_time = time.time()
    time.sleep(max(1/FPS - (end_time - start_time), 0))
