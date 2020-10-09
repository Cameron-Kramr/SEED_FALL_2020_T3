#Cameron Kramr
#10/09/2020
#EENG 350
#Section A 
#Computer Vision
#NOTE, this module requires pygame to be installed in order to run
#This file ties together all the project files and implements the program structure
import numpy as np
import multiprocessing as mp
import picamera
from picamera import array
import Aruco_Multi_Threading as amt
import time
import cv2
import detect_angle
import Pi_Comms_Multi_Threading as pcmt
import math

#Initialize Aruco parameters
cam_mtx = np.fromfile("Examples/Calibration/cam_mtx.dat").reshape((3,3))
dist_mtx = np.fromfile("Examples/Calibration/dist_mtx.dat")
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_7X7_250)
parameters = cv2.aruco.DetectorParameters_create()

#Initiate Multiprocessing Pipes used for interconnecting the threads
cv2_conn1, cv2_conn2 = mp.Pipe(duplex = True)
pygme_conn1, pygme_conn2 = mp.Pipe(duplex = True)
cv2_aruco_1_conn1, cv2_aruco_1_conn2 = mp.Pipe(duplex = True)
cv2_aruco_2_conn1, cv2_aruco_2_conn2 = mp.Pipe(duplex = True)
picam_conn1, picam_conn2 = mp.Pipe(duplex = True)
I2C_pipe_1, I2C_pipe_2 = mp.Pipe(duplex = True)

#Create Multiprocessing Objects
picam_thread = mp.Process(target = amt.picam_image_grabbler, args = (picam_conn2, [cv2_aruco_1_conn1, cv2_aruco_2_conn1], (640, 480), 60,))
py_thread = mp.Process(target = amt.pygame_aruco_display_manager, args = (pygme_conn2,))
cv2_detect_1 = mp.Process(target = amt.cv2_detect_aruco_routine, args = (cv2_aruco_1_conn2, aruco_dict, parameters,))
cv2_detect_2 = mp.Process(target = amt.cv2_detect_aruco_routine, args = (cv2_aruco_2_conn2, aruco_dict, parameters,))
cv2_pose = mp.Process(target  = amt.cv2_estimate_pose, args = (cv2_conn2, 0.025, cam_mtx, dist_mtx,))
PI_I2C = mp.Process(target = pcmt.I2C_Handler, args = (I2C_pipe_2, (2,16), 0x08,))

#Start All Helper Threads:
py_thread.start()
cv2_detect_1.start()
cv2_detect_2.start()
cv2_pose.start()
picam_thread.start()
PI_I2C.start()

#Main Variables:
FPS = 60
start_time = 0
LCD_FPS = 0.7
LCD_Start_Time = 0
angle_in = 0
LCD_OUTPUT = False
rotations = [0,0,0]
SetPoint_FPS = 60
Set_Start = 0


#Main Running Loop
while(True):
	old_start = start_time
	start_time = time.time()

	#print("FPS: " + str(int(amt.calc_fps(old_start, start_time))))

	#Wait for aruco detection threads to yield data and then send them to the estimate pose thread
	while(cv2_aruco_1_conn1.poll()):
		cv2_conn1.send(cv2_aruco_1_conn1.recv())
	while(cv2_aruco_2_conn1.poll()):
		cv2_conn1.send(cv2_aruco_2_conn1.recv())
	
	#Wait for pose thread to yield translation and rotation information
	while(cv2_conn1.poll()):
		LCD_OUTPUT = True
		
		#Collect the poses
		poses = cv2_conn1.recv()
		
		#Send poses to pygame thread
		pygme_conn1.send(poses)
		
		#Create the correct rotation matrix from condensed form of the first detected marker
		rot_mtx, jacob = cv2.Rodrigues(poses[0][1][0][0])
		
		#Find rotation from expanded rotation matrix
		rotations = detect_angle.calc_Euclid_Angle(rot_mtx) * 180/math.pi

	#Frame lock the rate that data is sent to the aruduino to get consistent data stream. Will loose some data points
	if(time.time() - Set_Start >= 1/SetPoint_FPS):
		Set_Start = time.time()
		#Send command and data to I2C thread
		I2C_pipe_1.send([pcmt.I2C_CMD.WRITE_ARDU, detect_angle.deg_2_byte(rotations[2])])

	#Frame lock the LCD information sending because the LCD can't update faster than 1 Hz due to speed limitations
	if(time.time() - LCD_Start_Time >= 1/LCD_FPS and LCD_OUTPUT):
		LCD_Start_Time = time.time()
		#Message = "ID: " + str(poses[0][0][0]) + " X:" + str(int(rotations[0])) + " Y:" + str(int(rotations[1])) + "\nZ: " + str(int(rotations[2]))

		#Request the actual angle from the arduino
		I2C_pipe_1.send([pcmt.I2C_CMD.FETCH_ANGLE,0])
		
		#Construct the message to be displayed on the LCD. Note, it uses an old version of the actual angle
		Message = "ID: " + str(poses[0][0][0]) + " Z: " + str(int(rotations[2])) + "\nAct: " + str(int(angle_in))

		#Print the message dispalyed for validation
		print(Message)
		
		#Send the command to print to the LCD and the message to be displayed
		I2C_pipe_1.send([pcmt.I2C_CMD.LCD_CLR_MSG, Message])

	#Poll the I2C pipe. At this point, the only data that will appear here is actual angle value
	if(I2C_pipe_1.poll()):
		angle_in = I2C_pipe_1.recv()


	#Lock FPS to not waste resources
	end_time = time.time()
	time.sleep(max(1/FPS - (end_time - start_time), 0))


