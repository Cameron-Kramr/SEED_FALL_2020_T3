import numpy as np
import scipy as sc
import time
from collections import deque
import matplotlib.pyplot as plt

#def resample(values, times)

class marker():
	def __init__(self, buff_len = 10):
		self.ID = -1
		
		self.Samp_Period = 1/60
		self.buff_len = buff_len
		
		#Create deques for position
		self.X_Pos = deque([0 for i in range(buff_len)])
		self.Y_Pos = deque([0 for i in range(buff_len)])
		self.Z_Pos = deque([0 for i in range(buff_len)])
		
		#Create deques for rotations
		self.X_Rot = deque([0 for i in range(buff_len)])
		self.Y_Rot = deque([0 for i in range(buff_len)])
		self.Z_Rot = deque([0 for i in range(buff_len)])
		
		#Create deque for sample times
		self.Times = deque([0 for i in range(buff_len)])
		
		#Create output/filtered variables
		self.tvec_filt = [0,0,0]
		self.rvec_filt = [0,0,0]
		
	#Sets the filter values for filtering
	def set_filter(function, b, a, x, axis =-1, padtype='odd',padlen=None,method='pad',irlen=None):
		self.fiilter = function
		self.b = b
		self.a = a
		self.x = x
		self.axis = axis
		self.padtype = padtype
		self.padlen = padlen
		self.method = method
		self.irlen = irlen
		
	#Appends to the front of the stack and pops off the last element
	def add_sample(self, tvec, rvec, time):
		self.X_Pos.appendleft(tvec[0])
		self.Y_Pos.appendleft(tvec[1])
		self.Z_Pos.appendleft(tvec[2])
		
		self.X_Rot.appendleft(rvec[0])
		self.Y_Rot.appendleft(rvec[1])
		self.Z_Rot.appendleft(rvec[2])
		
		self.X_Pos.pop()
		self.Y_Pos.pop()
		self.Z_Pos.pop()
		
		self.X_Rot.pop()
		self.Y_Rot.pop()
		self.Z_Rot.pop()
		
		self.Times.appendleft(time)
		self.Times.pop()
		
	def get_filtered_vecs():
		tvec = []
		tvec.append()

if(__name__ == "__main__"):
	plt.figure()
	tester = marker()
	tester.add_sample([11,12,13],[14,15,16],time.time())
	tester.add_sample([21,22,23],[24,25,26],time.time())
	tester.add_sample([31,32,33],[34,35,36],time.time())
	tester.add_sample([41,42,43],[44,45,46],time.time())
	tester.add_sample([51,52,53],[54,55,56],time.time())
	tester.add_sample([61,62,63],[64,65,66],time.time())
	tester.add_sample([71,72,73],[74,75,76],time.time())
	tester.add_sample([81,82,83],[84,85,86],time.time())
	tester.add_sample([91,92,93],[94,95,96],time.time())
	tester.add_sample([101,102,103],[104,105,106],time.time())
	tester.add_sample([111,112,113],[114,115,116],time.time())
	print("X_POS:~~~~~~~~~~~~~~")
	print(str(tester.X_Pos))
	print("Y_POS:~~~~~~~~~~~~~~")
	print(str(tester.Y_Pos))
	print("Z_POS:~~~~~~~~~~~~~~")
	print(str(tester.Z_Pos))
	print("X_Rot:~~~~~~~~~~~~~~")
	print(str(tester.X_Rot))
	print("Y_Rot:~~~~~~~~~~~~~~")
	print(str(tester.Y_Rot))
	print("Z_Rot:~~~~~~~~~~~~~~")
	print(str(tester.Z_Rot))
	print("Time:~~~~~~~~~~~~~~")
	print(str(tester.Times))
	
	'''
	x = np.array([1,2,3,4,5,6,7,8,9,10])
	x2 = x + np.random.normal(0,1,x.shape)
	
	y = x**2
	y2 = x2**2
	
	plt.plot(x,y)
	plt.plot(x2,y2)

	plt.show()
	h = input()
	'''
