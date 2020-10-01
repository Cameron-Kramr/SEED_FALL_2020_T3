import multiprocessing as mp
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import pygame
import math


def pygame_aruco_display_manager(input_pipe):

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
			inputs = input_pipe.recv()
			gameDisplay.fill((0,0,0))
			for i in inputs:
				#print("Pygame processing: " + str(i[0]))
				img = font.render("ID: " + str(i[0][0]), True, (255, 0, 0))
				px = int(i[2][0][0][0] * gain + width/2)
				py = int(height - i[2][0][0][2] * gain)
				pygame.draw.circle(gameDisplay, (255, 255, 255), (px, py), 10)
				gameDisplay.blit(img, (px, py - 10))
			#print("Pygame Done Processing")
		pygame.display.update()
		inputs = []

def cv2_estimate_pose(input_pipe, side_length, cam_mtx, dis_coefs):
	output = []
	input = []
	#count = 0

	while(True):
		#print("cv2 at: " + str(count))
		#count += 1
		#Expect data of shape:
		#([id, corners], ...)
		inputs = input_pipe.recv()

		for i in inputs:
			rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(i[1], side_length, cam_mtx,dis_coefs )
			output.append((i[0], rvecs, tvecs))
		input_pipe.send(output)
		output = []
#~~~~~~~~~~~~~~~~Initialize program~~~~~~~~~~~~~~~~~~~~#

#initialize the camera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
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

py_thread = mp.Process(target = pygame_aruco_display_manager, args=(pygme_conn2,))
cv2_thread = mp.Process(target = cv2_estimate_pose, args=(cv2_conn2, 0.025, camera_mtx, dist_mtx,))

py_thread.start()
cv2_thread.start()

count = 0

#allow camera to warmup
time.sleep(0.1)

#~~~~~~~~~~~~~~~~Main Code~~~~~~~~~~~~~~~~~~~~~~~~~~#

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port = True):
	#print("Main at: " + str(count))
	#count += 1

	start = time.time()

	frame_raw = frame.array
	frame_grey = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2GRAY)

	#Detect markers:
	start_detect = time.time()
	corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(frame_grey, aruco_dict, parameters = parameters)
	end_detect = time.time()

	print("Detect FPS: " + str(int(1/(end_detect - start_detect))))

	#Send information to proper thread
	if len(corners) != 0:
		cv_input = [(item, corners[iter]) for iter, item in enumerate(ids)]
		cv2_conn1.send(cv_input)

	#Draw and present results
	start_draw = time.time()
	cv2.aruco.drawDetectedMarkers(frame_raw, corners, ids)
	cv2.aruco.drawDetectedMarkers(frame_raw, rejectedImgPoints)
	cv2.imshow("Frame", frame_raw)
	end_draw = time.time()
	print("Draw FPS: " + str(int(1/(end_draw - start_draw))))


	rawCapture.truncate(0)

	key = cv2.waitKey(1)

	if key == 27:
		py_thread.kill()
		cv2_thread.kill()
		time.sleep(0.5)
		py_thread.close()
		py_thread.close()

		break

	#Check for new things from cv2 thread and sends them to pygame if they're there.

	while(cv2_conn1.poll(timeout = 0)):
		#print("Main sending data!")
		pygme_conn1.send(cv2_conn1.recv())
	end_time = time.time()
	print("FPS: " + str(int(1/(end_time-start))))
