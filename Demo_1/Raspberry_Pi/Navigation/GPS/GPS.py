import time
import numpy as np
import pygame as pg

class GPS_Node():
	def __init__(self, ID = -1):
		self.ID = ID
		#contains the relative translation vector from each other node this node has been seen with
		self.tvecs = dict()
		
		#Location of the node in the world coordinate system.
		self.World_Tvec = np.array([0,0,0])
		
		#Flag noting if the node has been located
		self.Located = False
		
	#Updates Tvecs between the nodes. Used to determine relative position
	def update_Node(self, nodes):
		#Nodes should be a dictionary containing all the seen nodes indexed at their id
		if(self.ID in nodes):
			for i in nodes:
				if(i != self.ID):
					#Check if it's been seen before.
					if(i in self.tvecs):
						#Perform a simple average if the values differ. This should be replaced with a more fit filter such as a kalman filter later)
						self.tvecs[i] = (self.tvecs[i] + nodes[i] - nodes[self.ID])/2
					else: #initiate the new node's relative location
						self.tvecs[i] = nodes[i] - nodes[self.ID]


class GPS_System():
	def __init__(self):
	
		#When system first initializes, need to establish a node as the world node
		self.World_Established = False
		
		#Stores all the seen nodes
		self.Nodes = dict()

	#Updates the nodes relative translation vectors
	def update_Nodes(self, nodes):
		for node in nodes:
			#Need to check that nodes are in list
			
			if(node in self.Nodes):
				self.Nodes[node].update_Node(nodes)
			#If nodes are not already known, create it
			else:
				self.Nodes[node] = GPS_Node(ID = node)
				self.Nodes[node].update_Node(nodes)

	#Updates the world position of all the nodes
	def locate_Node(self, nodes):
		for updating_node in self.Nodes:
			#Check to make sure updating node is in the frame of observed nodes
			if updating_node in nodes:
				#loop over all seen nodes which contain new information
				for other_node in nodes:
					#Check that we're not looking at the current node
					if(other_node != updating_node):
							#check to see if other node has been located first, otherwise it's useless and will be used once located
							if(self.Nodes[other_node].Located):
								

	#Updates the world
	def update_World(self, nodes):
		#Nodes should be a dictionary containing all the seen nodes indexed at their id

		#Establish a world reference if one does not exist yet
		if(not self.World_Established):
			self.Nodes[nodes.keys[0]] = GPS_Node(ID = nodes.keys[0])
			self.Nodes[nodes.keys[0]].World_Tvec = np.array([0,0,0])
			self.World_Established = True

		#Update the node's relative position, this ensures that some data is present about the nodes
		self.update_Nodes(nodes)

		for i in nodes:
			
	

	#Takes the Tvecs from visible nodes and uses them to compute the relative position
	def calc_position(self, nodes):
		#Nodes should be an iterable object shaped: [[ID, tvec], ...]
		#Where tvecs are the translation vectors from the observer to the node
		output = [self.Nodes[i[0]].tvec - i[1] for i in nodes]
		
		
if __name__ == "__main__":
	Global_Pos = GPS_System()
	N1 = GPS_Node(ID = 1)
	N2 = GPS_Node(ID = 2)
	
	tvec_1 = np.array([1,2,3])
	tvec_2 = np.array([2,4,6])
	tvec_3 = np.array([4,8,12])
	tvec_4 = np.array([8,16,24])
	
	new_nodes_1 = {1:tvec_1, 2:tvec_2, 3:tvec_3}
	new_nodes_2 = {1:tvec_3, 2:tvec_4, 3:tvec_1}
	
	N1.update_Node(new_nodes_1)
	N1.update_Node(new_nodes_2)
	
	
	
	