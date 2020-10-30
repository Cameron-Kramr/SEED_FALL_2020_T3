#Cameron Kramr
#10/09/2020
#EENG 350
#Section A 
#Computer Vision
#NOTE, this module requires pygame to be installed in order to run
#This file contains the subroutines that are used in the aruco marker detection scheme.

import multiprocessing as mp
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import pygame
import math

#Calculates the FPS
def calc_fps(start_time, end_time):
	return 1/(end_time-start_time)

#Display the aruco markers onto the pigame display
def pygame_aruco_display_manager(input_pipe, debug = False):
	#Initialize pygame objects
	pygame.init()
	gameDisplay = pygame.display.set_mode((800, 600))
	gameDisplay.fill((0,0,0))
	font = pygame.font.SysFont(None, 20)

	inputs = []

	gain = 1000
	width, height = pygame.display.get_surface().get_size()

	#count = 0

	#Infinite loop to handle drawing new frames of the locations of markers
	while(True):

		#expect data of this form:
		#[(id, rvecs, tvecs), ...])

		#Blocking wait for input into the pipe
		inputs = input_pipe.recv()
	
		#record the time
		start_time = time.time()
		
		#Clear the display
		gameDisplay.fill((0,0,0))
		
		#Loop over all the inputs of the form described above
		for i in inputs:
			#print("Pygame processing: " + str(i[0]))
			#create text image for showing the marker ID
			img = font.render("ID: " + str(i[0][0]), True, (255, 0, 0))
			
			#Find the position the marker should appear on the display
			px = int(i[2][0][0][0] * gain + width/2)
			py = int(height - i[2][0][0][2] * gain)
			#Draw the circle and blit the text onto the display
			pygame.draw.circle(gameDisplay, (255, 255, 255), (px, py), 10)
			gameDisplay.blit(img, (px, py - 10))
			
		#Record the end time 
		end_time = time.time()
		
		#Calculate the FPS the code runs at if in debugging mode
		if(debug):
			print("Pygame FPS: " + str(int(1/(end_time- start_time))))
			
		#Update the display with the new images and clear the input
		pygame.display.update()
		inputs = []

#Estimates the pose/position of a marker from the pipes
def cv2_estimate_pose(input_pipe, side_length, cam_mtx, dis_coefs, debug = False):
	output = []
	input = []
	#count = 0

	#Infinite loop runs subroutine until terminated by parent thread
	while(True):
		#Expect data of shape:
		#([id, corners], ...)
		#blocking wait on data to appear at input pipe
		inputs = input_pipe.recv()

		#Record the start time
		start_time = time.time()
		
		#Loop over the inputs received from the pipe
		for i in inputs:
			#Find the translation and rotation vectors. Object points less important
			rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(i[1], side_length, cam_mtx,dis_coefs )
			output.append([i[0], rvecs, tvecs])
		#Send output back to main thread for further processing
		input_pipe.send(output)
		
		#Clear output
		output = []
		
		#Record end time and print out if in debugging mode
		end_time = time.time()
		if(debug):
			print("Cv2 Pose FPS: " + str(int(1/(end_time - start_time))))


#Detects the aruco markers from image pipes
def cv2_detect_aruco_routine(input_pipe, aruco_dict, parameters, debug = False):

	output = []

	while(True):
		#Grab a frame
		frame_grab_start = time.time()
		frame = input_pipe.recv()
		frame_grab_end = time.time()
		
		#Convert to grey scale
		frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		#debug info
		if(debug):
			print("CV2 grab Frame FPS: " + str(int(calc_fps(frame_grab_start, frame_grab_end))))
		#Find the aruco markers
		corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(frame_grey, aruco_dict, parameters = parameters)

		#if any are present, send the data out
		if(len(corners) != 0):
			#construct & send output
			output = [(item, corners[iter]) for iter, item in enumerate(ids)]
			input_pipe.send(output)

#Grabblers the images and stuffs them into appropriate pipes
def picam_image_grabbler(inputpipe, image_pipes, resolution, frame_rate, format = "bgr"):
	#Pi camera setup
	camera = PiCamera()
	camera.resolution = resolution
	camera.framerate = frame_rate

	rawCapture = PiRGBArray(camera, size = resolution)
	#If there is only one pipe, make it into an array to not break future code
	if(not isinstance(image_pipes, (list,tuple))):
		image_pipes = [image_pipes]

	out_pipe_count = len(image_pipes)
	output_counter = 0

	#Capture the frames continuously from the camera
	for frame in camera.capture_continuous(rawCapture, format = format, use_video_port = True):
		#print("Grabbled Frame!")
		
		#send image down appropriate pipes
		image_pipes[output_counter].send(frame.array)
		output_counter += 1

		#Clear the pipe counter if necessary
		if(output_counter >= out_pipe_count):
			output_counter = 0

		#Clear this mmal buffer so it won't overflow
		rawCapture.truncate(0)

		start = time.time()
