import multiprocessing as mp
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import pygame
import math


def calc_fps(start_time, end_time):
	return 1/(end_time-start_time)

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
		if(input_pipe.poll()):
			start_time = time.time()
			inputs = input_pipe.recv()
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

def cv2_estimate_pose(input_pipe, side_length, cam_mtx, dis_coefs, debug = False):
	output = []
	input = []
	#count = 0

	while(True):
		#print("cv2 at: " + str(count))
		#count += 1
		#Expect data of shape:
		#([id, corners], ...)
		inputs = input_pipe.recv()

		start_time = time.time()
		for i in inputs:
			rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(i[1], side_length, cam_mtx,dis_coefs )
			output.append((i[0], rvecs, tvecs))
		input_pipe.send(output)
		output = []
		end_time = time.time()
		if(debug):
			print("Cv2 Pose FPS: " + str(int(1/(end_time - start_time))))

def cv2_detect_aruco_routine(input_pipe, aruco_dict, parameters, debug = False):

	output = []

	while(True):
		if(input_pipe.poll()):
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

#~~~~~~~~~~~~~~~~Initialize program~~~~~~~~~~~~~~~~~~~~#

#initialize the camera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 60
rawCapture = PiRGBArray(camera, size=(640, 480))

#load distortion and camera matrices from calibration script
camera_mtx = np.fromfile("Calibration/cam_mtx.dat").reshape((3,3))
dist_mtx = np.fromfile("Calibration/dist_mtx.dat")

#initialize the Aruco Detection parameters
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_7X7_250)
parameters = cv2.aruco.DetectorParameters_create()

#Create multiprocessing objects
cv2_conn1, cv2_conn2 = mp.Pipe(duplex = True)
pygme_conn1, pygme_conn2 = mp.Pipe(duplex = True)
cv2_aruco_1_conn1, cv2_aruco_1_conn2 = mp.Pipe(duplex = True)
cv2_aruco_2_conn1, cv2_aruco_2_conn2 = mp.Pipe(duplex = True)

#Create mulitprocessing threads
py_thread = mp.Process(target = pygame_aruco_display_manager, args=(pygme_conn2,))
cv2_thread = mp.Process(target = cv2_estimate_pose, args=(cv2_conn2, 0.025, camera_mtx, dist_mtx,))
cv2_aruco_1_thread = mp.Process(target = cv2_detect_aruco_routine, args=(cv2_aruco_1_conn2, aruco_dict, parameters, False,))
cv2_aruco_2_thread = mp.Process(target = cv2_detect_aruco_routine, args=(cv2_aruco_2_conn2, aruco_dict, parameters, False,))

#Startup threads
py_thread.start()
cv2_thread.start()
cv2_aruco_1_thread.start()
cv2_aruco_2_thread.start()

#User variables:
count = 0
thread_1 = True

#allow camera to warmup
time.sleep(0.1)

#~~~~~~~~~~~~~~~~Main Code~~~~~~~~~~~~~~~~~~~~~~~~~~#

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port = True):
	#print("Main at: " + str(count))
	#count += 1

	start = time.time()

	#send frame data
	if(thread_1):
		cv2_aruco_1_conn1.send(frame.array)
	else:
		cv2_aruco_2_conn1.send(frame.array)
	thread_1 = not thread_1

	#Send information if it's there
	if cv2_aruco_1_conn1.poll():
		cv2_conn1.send(cv2_aruco_1_conn1.recv())
	if cv2_aruco_2_conn1.poll():
		cv2_conn1.send(cv2_aruco_2_conn1.recv())

	#Clear buffer
	rawCapture.truncate(0)

	#Check for new things from cv2 thread and sends them to pygame if they're there.
	while(cv2_conn1.poll(timeout = 0)):
		#print("Main sending data!")
		pygme_conn1.send(cv2_conn1.recv())
	end_time = time.time()
	print("Main FPS: " + str(int(1/(end_time-start))))
