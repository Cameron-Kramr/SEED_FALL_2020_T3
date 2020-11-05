#Cameron Kramr
#10/09/2020
#EENG 350
#Section A
#Computer Vision
#NOTE, this module requires pygame to be installed in order to run
#This file ties together all the project files and implements the program structure

import sys
import numpy as np
import multiprocessing as mp
import picamera
from picamera import array
import Detection.Aruco_Multi_Threading as amt
import time
import cv2
import Detection.detect_angle as dta
import Comms.Pi_Comms_Multi_Threading as pcmt
import math

#Initialize Aruco parameters
cam_mtx = np.fromfile("Navigation/Camera_Utils/cam_mtx.dat").reshape((3,3))
dist_mtx = np.fromfile("Navigation/Camera_Utils/dist_mtx.dat")
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_7X7_250)
parameters = cv2.aruco.DetectorParameters_create()

#Initiate Multiprocessing Pipes used for interconnecting the threads
cv2_conn1, cv2_conn2 = mp.Pipe(duplex = True)
pygme_conn1, pygme_conn2 = mp.Pipe(duplex = True)
cv2_aruco_1_conn1, cv2_aruco_1_conn2 = mp.Pipe(duplex = True)
cv2_aruco_2_conn1, cv2_aruco_2_conn2 = mp.Pipe(duplex = True)
picam_conn1, picam_conn2 = mp.Pipe(duplex = True)
I2C_pipe_1, I2C_pipe_2 = mp.Pipe(duplex = True)
ARDU_pipe_1, ARDU_pipe_2 = mp.Pipe(duplex = True)

#Create Multiprocessing Objects
picam_thread = mp.Process(target = amt.picam_image_grabbler, args = (picam_conn2, [cv2_aruco_1_conn1, cv2_aruco_2_conn1], (640, 480), 60,))
py_thread = mp.Process(target = amt.pygame_aruco_display_manager, args = (pygme_conn2,))
cv2_detect_1 = mp.Process(target = amt.cv2_detect_aruco_routine, args = (cv2_aruco_1_conn2, aruco_dict, parameters,))
cv2_detect_2 = mp.Process(target = amt.cv2_detect_aruco_routine, args = (cv2_aruco_2_conn2, aruco_dict, parameters,))
cv2_pose = mp.Process(target  = amt.cv2_estimate_pose, args = (cv2_conn2, 0.1, cam_mtx, dist_mtx,))
PI_I2C = mp.Process(target = pcmt.I2C_Handler, args = (I2C_pipe_2, (2,16), 0x08,))
PI_ARDU = mp.Process(target = pcmt.Serial_Handler, args = (ARDU_pipe_2,))

#Start All Helper Threads:
#py_thread.start()
cv2_detect_1.start()
cv2_detect_2.start()
cv2_pose.start()
picam_thread.start()
#PI_I2C.start()
#PI_ARDU.start()

pcmt.init_anykey()

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
    old_start = start_time
    start_time = time.time()

    #print("FPS: " + str(int(amt.calc_fps(old_start, start_time))))

    #While aruco detection threads to yield data, send them to the estimate pose thread
    while(cv2_aruco_1_conn1.poll()):
        cv2_conn1.send(cv2_aruco_1_conn1.recv())
    while(cv2_aruco_2_conn1.poll()):
        cv2_conn1.send(cv2_aruco_2_conn1.recv())

    #While pose thread yields translation and rotation information, process it
    while(cv2_conn1.poll()):
        LCD_OUTPUT = True

        #Collect the poses
        poses = cv2_conn1.recv()

        #Send poses to pygame thread
        #pygme_conn1.send(poses)

        #Create the correct rotation matrix from condensed form of the first detected marker
        rot_mtx, jacob = cv2.Rodrigues(poses[0][1][0][0])

        #Find rotation from expanded rotation matrix
        rotations = dta.calc_Euclid_Angle(rot_mtx) * 180/math.pi

    #Frame lock the rate that data is sent to the aruduino to get consistent data stream. Will loose some data points
    if(time.time() - Ardu_Start >= 1/Ardu_FPS):
        Ardu_Start = time.time()
        #Send command and data to Arduino thread
        if(terminal_msg != None):
            #ARDU_pipe_1.send([pcmt.ARDU_CMD.SEND, terminal_msg])
            terminal_msg = None
        if(compound and time.time() > compound_start + compound_time):
            print("sending compounding movement")
            compound = False
            #ARDU_pipe_1.send([pcmt.ARDU_CMD.SEND, "1 0"])

    #Frame lock the LCD information sending because the LCD can't update faster than 1 Hz due to speed limitations
    if(time.time() - LCD_Start_Time >= 1/LCD_FPS and LCD_OUTPUT):
        LCD_Start_Time = time.time()
        #Message = "ID: " + str(poses[0][0][0]) + " X:" + str(int(rotations[0])) + " Y:" + str(int(rotations[1])) + "\nZ: " + str(int(rotations[2]))

        #Construct the message to be displayed on the LCD. Note, it uses an old version of the actual angle
        print(str(poses[0][2][0][0]))
        #print(str(poses[0][2][0][0][2]))
        angle = math.atan2(poses[0][2][0][0][2], poses[0][2][0][0][0])*180/math.pi - 90
        print(angle)
        Message = "ID: " + str(poses[0][0][0]) + "\nX: " + str(angle)

        #Print the message dispalyed for validation
        #print(Message)

        #Send the command to print to the LCD and the message to be displayed
        #I2C_pipe_1.send([pcmt.I2C_CMD.LCD_CLR_MSG, Message])

    #Poll the Serial pipe.
    if(ARDU_pipe_1.poll()):
        ardu_data = ARDU_pipe_1.recv()
        print("Arduino Echo:")
        print(ardu_data)

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


cv2_detect_1.kill()
cv2_detect_2.kill()
cv2_pose.kill()
picam_thread.kill()
