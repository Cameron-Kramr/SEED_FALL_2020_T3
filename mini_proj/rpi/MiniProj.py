import numpy as np
import multiprocessing as mp
import picamera
from picamera import array
import Aruco_Multi_Threading as amt
import time
import cv2

#Initialize Aruco parameters
cam_mtx = np.fromfile("Examples/Calibration/cam_mtx.dat").reshape((3,3))
dist_mtx = np.fromfile("Examples/Calibration/dist_mtx.dat")
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_7X7_250)
parameters = cv2.aruco.DetectorParameters_create()

#Initiate Multiprocessing Components
cv2_conn1, cv2_conn2 = mp.Pipe(duplex = True)
pygme_conn1, pygme_conn2 = mp.Pipe(duplex = True)
cv2_aruco_1_conn1, cv2_aruco_1_conn2 = mp.Pipe(duplex = True)
cv2_aruco_2_conn1, cv2_aruco_2_conn2 = mp.Pipe(duplex = True)
picam_conn1, picam_conn2 = mp.Pipe(duplex = True)

#Create Multiprocessing Objects
picam_thread = mp.Process(target = amt.picam_image_grabbler, args = (picam_conn2, [cv2_aruco_1_conn1, cv2_aruco_2_conn1], (640, 480), 60,))
py_thread = mp.Process(target = amt.pygame_aruco_display_manager, args = (pygme_conn2,))
cv2_detect_1 = mp.Process(target = amt.cv2_detect_aruco_routine, args = (cv2_aruco_1_conn2, aruco_dict, parameters,))
cv2_detect_2 = mp.Process(target = amt.cv2_detect_aruco_routine, args = (cv2_aruco_2_conn2, aruco_dict, parameters,))
cv2_pose = mp.Process(target  = amt.cv2_estimate_pose, args = (cv2_conn2, 0.025, cam_mtx, dist_mtx,))

#Start All Helper Threads:
py_thread.start()
cv2_detect_1.start()
cv2_detect_2.start()
cv2_pose.start()
picam_thread.start()

#Main Variables:
FPS = 60
start_time = 0

#Main Running Loop
while(True):
	old_start = start_time
	start_time = time.time()

	print("FPS: " + str(int(amt.calc_fps(old_start, start_time))))

	while(cv2_aruco_1_conn1.poll()):
		cv2_conn1.send(cv2_aruco_1_conn1.recv())
	while(cv2_aruco_2_conn1.poll()):
		cv2_conn1.send(cv2_aruco_2_conn1.recv())
	while(cv2_conn1.poll()):
		pygme_conn1.send(cv2_conn1.recv())

	#Lock FPS
	end_time = time.time()
	time.sleep(max(1/FPS - (end_time - start_time), 0))

