#Cameron Kramr
#9/20/2020
#EENG 350
#Section A 
#Computer Vision
#NOTE, this module requires pygame to be installed in order to run

"""~~~~~~~~~~~~~Exercise 6-7~~~~~~~~~~~~~"""

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import pygame
import math

#pygame is used for visualization of position in 2D space
pygame.init()

#init some pygame variables
gameDisplay = pygame.display.set_mode((800,600))
gameDisplay.fill((0,0,0))


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

#load distortion and camera matrices from calibration script
camera_mtx = np.fromfile("Calibration/cam_mtx.dat").reshape((3,3))
dist_mtx = np.fromfile("Calibration/dist_mtx.dat")

# initialize the Aruco Detection parameters
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_7X7_250)
parameters = cv2.aruco.DetectorParameters_create()

# allow the camera to warmup
time.sleep(0.1)


#Function to determine the position information
def Estimate_Aruco_Location(markerCorners, side_length, cameraMatrix, distCoeffs, id = None):

	#Get position descriptors using camera and distortion matrices from calibration
	rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(markerCorners, side_length, cameraMatrix, distCoeffs)
	#convert rotation vector to rotation matrix
	rot_mtx, jacob = cv2.Rodrigues(rvecs)
	#extract euler angles to know rotation around the axii
	euler_angles = rotationMatrixToEulerAngles(rot_mtx)
	#print("R: "str(rvecs))

	#if no id provided, skip this step
	if id != None:
		#Show the magnitude of the distance from the marker
		#Tvec is the translation vector from the center of the markers to the center of the camera
		print(str(id) + "dist: " + str(np.linalg.norm(tvecs)))
		print(str(id) + "cord: " + str(tvecs))
		#convert radians to degrees for human units
		print(str(id) + "angl: " + str(euler_angles*180/math.pi))
	return rvecs, tvecs

#Function for converting rotation matrices to euler angles
def rotationMatrixToEulerAngles(R):
	#assert(cv2.isRotationMatrix(R))
	#print(R)

	sy = math.sqrt(R[0,0] * R[0,0] + R[1,0] * R[1,0])
	singular = sy < 1e-6
	if not singular:
		x = math.atan2(R[2,1],R[2,2])
		y = math.atan2(-R[2,0],sy)
		z = math.atan2(R[1,0],R[0,0])
	else:
		x = math.atan2(R[1,2],R[2,2])
		y = math.atan2(-R[2,0],sy)
		z = 0

	return np.array([x,y,z])

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port = True):
	start = time.time()	#timing for stats
	gain = 1000	#physical position to pixel position on pygame visualizer

	# grab the raw NumPy array representing the image - this array
	#print(type(frame))
	frame_raw = frame.array
	#make a grey copy
	frame_grey = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2GRAY)

	#find the aruco points in the provided image
	corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(frame_grey, aruco_dict, parameters = parameters)

	#Stuff to do when aruco present
	if len(corners) != 0:
		#clear visualizer screen
		gameDisplay.fill((0,0,0))
		w, h = pygame.display.get_surface().get_size()

		#for each aruco found
		for iter, item in enumerate(ids):

			#get position data
			rvecs, tvecs = Estimate_Aruco_Location(corners[iter], 0.025, camera_mtx, dist_mtx, id = item)

			#draw positions on visualizer
			pygame.draw.circle(gameDisplay, (255,255,255), (int(tvecs[0][0][0]*gain + w/2), int(tvecs[0][0][2]*gain)), 10)

	#draw the detected and potential markers on the cv screen
	cv2.aruco.drawDetectedMarkers(frame_raw, corners, ids)
	cv2.aruco.drawDetectedMarkers(frame_raw, rejectedImgPoints)

	#image = frame_raw
	# show the frame

	#show the frames and update the visualizer
	cv2.imshow("Frame", frame_raw)
	pygame.display.update()

	#wait to see if a key is pressed
	key = cv2.waitKey(1) & 0xFF

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

	#calculate and print timing stats
	endtime = time.time()
	print('\f %d fps' % int(1/(endtime - start)))

pygame.quit()

