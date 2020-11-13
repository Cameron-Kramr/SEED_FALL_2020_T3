#Cameron Kramr
#9/20/2020
#EENG 350
#Section A 
#Computer Vision

"""~~~~~~~~ Calibration Script ~~~~~~~~~~~~"""

import io
import picamera as pc
from picamera.array import PiRGBArray
import numpy as np
import cv2
import time




def gather_points(num_captures, name, camera = None, patternSize = None, patternSpace = 0.02):
	if not camera:
		camera = pc.PiCamera()
		camera.resolution = (640, 480)
		camera.framerate = 30
		cv2.waitKey(10)

	if not patternSize:
		patternSize = (7,9)

	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 0.030, 0.001)
	rawCapture = PiRGBArray(camera, size = (640,480))
	img_points = []
	obj_points = []

	# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
	objp = np.zeros((1,patternSize[0] * patternSize[1], 3), np.float32)
	objp[0,:,:2] = np.mgrid[0:patternSize[0],0:patternSize[1]].T.reshape(-1,2)*patternSpace

	for frame in camera.capture_continuous( rawCapture, format = "bgr", use_video_port = True):
		frame_BGR = frame.array
		frame_raw = cv2.cvtColor(frame_BGR, cv2.COLOR_BGR2GRAY)
		start = time.time()
		retval, corners = cv2.findChessboardCorners(frame_raw, patternSize)
		end = time.time()

		if retval:
			img_points.append(corners)
			obj_points.append(objp)

			cv2.drawChessboardCorners(frame_BGR, patternSize, corners, True)
			cv2.imshow("Detection", frame_BGR)
			key = cv2.waitKey(500)
		else:
			cv2.imshow("Detection", frame_BGR)
			key = cv2.waitKey(1)

		rawCapture.truncate(0)

		if(key == 27 or len(img_points) == num_captures):
			#print((obj_points))
			#print((img_points))
			ret, cam_mtx, dist, rvecs, tvecs, = cv2.calibrateCamera(obj_points, img_points, frame_raw.shape[::-1], None, None)
			return ret, cam_mtx, dist, rvecs, tvecs
		print(end - start)

if (__name__ == "__main__"):
	ret, cam_mtx, dist, rvecs, tvecs = gather_points(20, "joe", patternSpace = 0.02)
	#print(cam_mtx)
	#print(dist)

	cam_mtx.tofile("cam_mtx.dat")

	dist.tofile("dist_mtx.dat")

	#rvecs.tofile("rvecs_mtx.dat")
