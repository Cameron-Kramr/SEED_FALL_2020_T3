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

		inputs = input_pipe.recv()
		start_time = time.time()
		gameDisplay.fill((0,0,0))
		for i in inputs:
			#print("Pygame processing: " + str(i[0]))
			img = font.render("ID: " + str(i[0][0]), True, (255, 0, 0))
			px = int(i[2][0][0][0] * gain + width/2)
			py = int(height - i[2][0][0][2] * gain)
			pygame.draw.circle(gameDisplay, (255, 255, 255), (px, py), 10)
			gameDisplay.blit(img, (px, py - 10))
		end_time = time.time()
		if(debug):
			print("Pygame FPS: " + str(int(1/(end_time- start_time))))
		pygame.display.update()
		inputs = []

#Estimates the pose/position of a marker from the pipes
def cv2_estimate_pose(input_pipe, side_length, cam_mtx, dis_coefs, debug = False):
	output = []
	input = []
	#count = 0

	while(True):
		#Expect data of shape:
		#([id, corners], ...)
		inputs = input_pipe.recv()

		start_time = time.time()
		for i in inputs:
			rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(i[1], side_length, cam_mtx,dis_coefs )
			output.append([i[0], rvecs, tvecs])
		input_pipe.send(output)
		output = []
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

		frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		#debug info
		if(debug):
			print("CV2 grab Frame FPS: " + str(int(calc_fps(frame_grab_start, frame_grab_end))))
		corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(frame_grey, aruco_dict, parameters = parameters)

		if(len(corners) != 0):
			#construct & send output
			output = [(item, corners[iter]) for iter, item in enumerate(ids)]
			input_pipe.send(output)

#Grabblers the images and stuffs them into appropriate pipes
def picam_image_grabbler(inputpipe, image_pipes, resolution, frame_rate, format = "bgr"):
	camera = PiCamera()
	camera.resolution = resolution
	camera.framerate = frame_rate

	rawCapture = PiRGBArray(camera, size = resolution)

	if(not isinstance(image_pipes, (list,tuple))):
		image_pipes = [image_pipes]

	out_pipe_count = len(image_pipes)
	output_counter = 0

	for frame in camera.capture_continuous(rawCapture, format = format, use_video_port = True):
		#print("Grabbled Frame!")
		#send image down appropriate pipes
		image_pipes[output_counter].send(frame.array)
		output_counter += 1

		#Clear the pipe counter if necessary
		if(output_counter >= out_pipe_count):
			output_counter = 0

		rawCapture.truncate(0)

		start = time.time()
