import time
import numpy as np
import pygame as pg
import matplotlib


class GPS_System():
	def __init__(self):
	
		#When system first initializes, need to establish a node as the world node
		self.World_Established = False
		
		#Stores all the seen nodes and their position in the node matrix
		self.Nodes = dict()
		
		#Node Position Matrices
		self.Tnode = np.zeros()	#Node Relative Matrix
		self.Tw = np.zeros()	#Node Relative to world matrix
		
		self.Q
		self.R = 
		
		self.K
		
		self.H
		self.B
		
		self.P
		
	#adds new node into node dictionary and updates all required matrices
	def addNode(self, node):
		if not node in self.Nodes:
			
	#Returns the XYZ position of the node in the world.
	def getNodeWorldPos(self, node):
		return np.array(self.Tw[:, self.Nodes[node]])
		
		
if __name__ == "__main__":
	Global_Pos = GPS_System()

	
	
	
	