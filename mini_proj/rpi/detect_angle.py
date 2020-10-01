import math
import numpy as np

def detect_angle(corners):
	avg = sum(corners)/len(corners)
	return math.atan2(avg[1],avg[0])*180/math.pi

def 

if(__name__ == "__main__"):
	g = np.zeros((4,2))
	g[0] = (0,1)
	g[1] = (1,1)
	g[2] = (1,0)
	g[3] = (0,0)

	print(detect_angle(g))
