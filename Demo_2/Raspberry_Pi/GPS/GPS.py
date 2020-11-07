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
		self.Tnode = np.zeros((3,1,1))	#Node Relative Matrix
		self.Tw = np.zeros((3,1))	#Node Relative to world matrix
		
		#Covariance matrices
		self.Q = np.zeros((3,1,1))
		self.R = np.zeros((3,1,1))
		
		self.K = np.zeros((3,1,1))
		self.P = np.zeros((3,1,1))
		
		self.default_K = 0
		self.default_R = 1
		self.default_Q = 2
		self.default_P = 3
		
	def calc_Tnode(self, nodes):
		for i in nodes:
			for j in nodes:
				if(j != i):
					diff = np.array(i[1]) - np.array(j[1])
					self.Tnode[:,self.Nodes[i[0]], self.Nodes[j[0]]] = diff
					self.Tnode[:,self.Nodes[j[0]], self.Nodes[i[0]]] = -diff
		
	def update(self, nodes):
		for i in nodes:
			if(not i[0] in self.Nodes):
				self.add_Node(i, nodes)
				
		self.calc_Tnode(nodes)

	def calc_node_Tw(self, nodes, node = (-1,[0,0,0])):
		output = np.zeros((3,1))
		count = len(nodes)
		
		print(nodes)
		
		for i in nodes:
			if(node[0] != i[0] and i[0] in self.Nodes):
				output[:,0] += (self.Tw[:,self.Nodes[i[0]]] - i[1] + node[1])
				#print(output)
				#print("*********")
			else:
				count -= 1
		#print("DONE CAlculating")
		return output/count

	#Establishes the world
	def Establish_World(self, node):
		if(self.World_Established == False):
			self.Nodes[0] = node[0]
			
			#Node is at it's translation vector
			self.Tw[:,0] = node[1]
			
			#Create proper arrays
			self.Q[:,0,0] = self.default_Q
			self.R[:,0,0] = self.default_R
			self.K[:,0,0] = self.default_K
			self.P[:,0,0] = self.default_P
			
	#adds new node into node dictionary and updates all required matrices
	def add_Nodes(self, nodes):
		for node in nodes:
			if not node[0] in self.Nodes:
				index = len(self.Nodes)
				self.Nodes[node[0]] = index
				
				#Don't do this if the world isn't established
				if(self.World_Established):
					self.K = np.insert(np.insert(self.K, index, 0, axis = 1), index, 0, axis = 2)
					self.R = np.insert(np.insert(self.R, index, 0, axis = 1), index, 0, axis = 2)
					self.Q = np.insert(np.insert(self.Q, index, 0, axis = 1), index, 0, axis = 2)
					self.P = np.insert(np.insert(self.P, index, 0, axis = 1), index, 0, axis = 2)
					self.Tnode = np.insert(np.insert(self.Tnode, index, 0, axis = 1), index, 0, axis = 2)
					
					#Add translation vectors
					self.Tw = np.insert(self.Tw, index, 0, axis = 1)
					self.Tw[:, index] = self.calc_node_Tw(nodes, node = node)[:,0]
					
				else:
					self.World_Established = True
					self.Tw[:,0] = node[1]
				
				#Set Default Values
				self.K[:,index,index] = self.default_K
				self.R[:,index,index] = self.default_R
				self.Q[:,index,index] = self.default_Q
				self.P[:,index,index] = self.default_P
			
			
			
			
			
	#Returns the XYZ position of the node in the world.
	def get_NodeWorld_Pos(self, node):
		return np.array(self.Tw[:, self.Nodes[node]])
		
		
if __name__ == "__main__":
	node_1 = (1, [2, 6, 3])
	node_2 = (2, [2, 2, 8])
	node_3 = (3, [2, 3, 3])
	node_4 = (4, [2, 2, 4])
	
	nodes = [node_1, node_2, node_3, node_4]
	
	Global_Pos = GPS_System()
	
	Global_Pos.add_Nodes(nodes)

	Global_Pos.calc_Tnode(nodes)
	
	#print(str(Global_Pos.Tnode))
	print(str(Global_Pos.Tw))
	print(str(Global_Pos.calc_node_Tw(nodes)))
	
	
	
	