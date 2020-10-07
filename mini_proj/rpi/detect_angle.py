import math
import numpy as np

#Averages the position of all the corners given and returns the angle relative to the x-axis
def detect_angle(corners):
	avg = sum(corners)/len(corners)
	if(avg[0] >= 0):
		return math.atan2(avg[1],avg[0])*180/math.pi
	else:
		return math.pi - math.atan2(avg[1],avg[0])*180/math.pi

def deg_2_byte(val):
	return int(val/180*128)

#Calculates the Euclidean Angle given the rvecs
def calc_Euclid_Angle(rvec):
	sy = math.sqrt(rvec[0,0]**2 + rvec[1,0]**2)
	if not (sy < 1e-6):
		x = math.atan2(rvec[2,1],rvec[2,2])
		y = math.atan2(-rvec[2,0],sy)
		z = math.atan2(rvec[1,0],rvec[0,0])
	else:
		x = math.atan2(rvec[1,2],rvec[2,2])
		y = math.atan2(-rvec[2,0],sy)
		z = 0
	return np.array([x,y,z])

if(__name__ == "__main__"):
	g = np.zeros((4,2))
	g[0] = (0,1)
	g[1] = (1,1)
	g[2] = (1,0)
	g[3] = (0,0)

	print(detect_angle(g))
