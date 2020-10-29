#Vector Flow Path finding
#Written By: Cameron Kramr
#Date: 08/25/2020
#EENG 350
#References:http://leifcell.com/2013/12/flow-field-pathfinding/
#https://gamedevelopment.tutsplus.com/tutorials/understanding-goal-based-vector-field-pathfinding--gamedev-9007
#http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter23_Crowd_Pathfinding_and_Steering_Using_Flow_Field_Tiles.pdf
#https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

#This code generates a vector field based on cost that can be used for navigation. To use it, simply run the code. If you want to
#Change the path, edit the cost field as is done below. Changing these values will cause the vector field to be different and
#So make a different path. This code generates the shortest path toward the goal for every possible starting position.
#The results can be verified in the output by looking at the second graph which shows the Integration function. 
#If you start at any point on this plot, following the neighbour with the lowest value will lead to the goal (default (0,0)).
#The last graph shows the cell that each cell leads to. These are done by ID and so can be difficult to follow.
#This algorithm can be slow for large areas

from array import array
import sys
import math
import time
import pygame
from collections import deque

#Field container for field operations
class Field:
	#Class initializer creates variables used later
	def __init__(self, X_size = 1, Y_size = 1, type = 'i', default_value = 0):

		self.Field = array(type, [default_value for i in range(X_size * Y_size)] )
		
		self.X_size = X_size
		self.Y_size = Y_size
		self.type = type

	#String override used to print out fields to console
	def __str__(self):
		output = ""
		#Iterate over every element
		for i in range(self.Y_size):
			for j in range(self.X_size):
				output += str(round(self.get(j,i), 3)) + '\t' #Convert each value to string
			output += '\n' #return carriage evertime we need it
		return output

	def copy(self):
		copy = array(self.type, [self.Field[i] for i in range(self.X_size * self.Y_size)] )
		return copy

	#Method sets the field to a single value
	def set_all(self, value = 0):
		output = ""
		#iterate over every element
		for i in range(self.X_size):
			for j in range(self.Y_size):
				self.set(i,j,value) #Set each value to the uniform value
	
	#Sets an element in the field to a value
	def set(self, xpos, ypos, value):
		self.Field[xpos + ypos*self.X_size] = value
	
	#Gets the value of an element in the field
	def get(self, xpos, ypos):
		return self.Field[xpos + ypos * self.X_size]
	
	#Finds the smallest value in a field that is not in the selected field
	#Selected field consists of 0's for unselected/visited cells and 1's for visited cells
	def find_smallest_not_selected(self, selected):
		smallest = sys.float_info.max   #Initialize this to the maximum
		x_out = 0
		y_out = 0

		#Iterate over the entire list
		for i in range(self.X_size):
			for j in range(self.Y_size):
				if(self.get(i,j) <= smallest and selected.get(i,j) != 1):
					x_out = i
					y_out = j
					smallest = self.get(i,j)
		return [x_out, y_out]

#Flow field container
class Flow_Field:
	
	#Initializes the class creates variables used later
	def __init__(self, X_size = 1, Y_size = 1, goal_x = 0, goal_y = 0, start_cost = 255):
		self.Cost		 =   Field(X_size, Y_size, 'f', start_cost)
		#self.temp_Cost		 =   Field(X_size, Y_size, 'f', start_cost)
		
		self.Integration  =   Field(X_size, Y_size, 'f', 0)
		self.Flow		 =   Field(X_size, Y_size, 'I', 0)
		
		self.X_size = X_size
		self.Y_size = Y_size

		self.X_goal = goal_x
		self.Y_goal = goal_y
	
	#Gets the value of an element in the field
	def get_heuristic(self, xpos, ypos):
		return math.sqrt((xpos-self.X_goal)**2 + (ypos-self.Y_goal)**2)

	def get_ID(self, xpos, ypos = None):
		if(ypos == None):
			xpos, ypos = xpos
		return xpos + self.X_size*ypos

	def get_XY(self, ID):
		xpos = (ID) % self.X_size
		return (int(xpos), int(((ID) - xpos) / self.X_size))

	def check_in_bounds(self, ID):
		xpos, ypos = self.get_XY(ID)
			
		return self.check_in_XY_Bounds(self, xpos, ypos)

	def check_in_XY_Bounds(self, xpos, ypos):
		if(xpos >= self.X_size or ypos >= self.Y_size or ypos < 0 or xpos < 0):
			return -1
		else:
			return self.get_ID(xpos, ypos)

	def get_neighbours(self, ID):
		#if(type(ID) == int):
		(xpos, ypos) = self.get_XY(ID)
		#else:
		#	(xpos, ypos) = ID
			
		output =[self.check_in_XY_Bounds(xpos + 1, ypos), self.check_in_XY_Bounds(xpos - 1, ypos), self.check_in_XY_Bounds(xpos, ypos + 1), self.check_in_XY_Bounds(xpos, ypos - 1), 
					self.check_in_XY_Bounds(xpos + 1, ypos + 1), self.check_in_XY_Bounds(xpos + 1, ypos - 1), self.check_in_XY_Bounds(xpos - 1, ypos + 1), self.check_in_XY_Bounds(xpos +-1, ypos - 1)]
		
		while(-1 in output):
			output.remove(-1)
			
		#print(output)
		return output

	def calc_integration(self):
		#Set the Integration list to max just like 
		self.Integration.set_all(sys.float_info.max)
		self.Integration.set(self.X_goal, self.Y_goal, 0)	
		
		openList = deque();
		openList.append(self.get_ID(self.X_goal, self.Y_goal))
		
		while(True):
			if(len(openList) == 0 ):
				break;
			working = openList.popleft()
			
			neighbours = self.get_neighbours(working)
			#print(neighbours)
			for i in neighbours:
				ix, iy = self.get_XY(i)
				#print(self.get_heuristic(ix, iy))
				newval = self.Cost.Field[i] + self.Integration.Field[working]# + self.get_heuristic(ix, iy)
				
				if newval < self.Integration.Field[i]:
					#print(newval)
					#print(self.Integration.Field[i])
					self.Integration.Field[i] = newval
					if(not i in openList):
						openList.appendleft(i)

	def calc_flow(self):
		for cell in range(self.X_size*self.Y_size):
			smallest = sys.float_info.max
			neighbours = self.get_neighbours(cell)
			
			for neigh in neighbours:
				if(self.Integration.Field[neigh] < smallest):
					smallest = self.Integration.Field[neigh]
					self.Flow.Field[cell] = neigh

#Display the aruco markers onto the pigame display
def pygame_flow_field_display(flow_field):
	#Initialize pygame objects
	pygame.init()
	gameDisplay = pygame.display.set_mode((800, 600))
	gameDisplay.fill((0,0,0))
	font = pygame.font.SysFont(None, 15)

	inputs = []

	width, height = pygame.display.get_surface().get_size()

	color_gain = int(255/max(flow_field.Integration.Field))
	gain = 20
	
	#Infinite loop to handle drawing new frames of the locations of markers
		#Clear the display
	gameDisplay.fill((0,0,0))
	
	x_offset = int(gain/2)
	y_offset = int(gain/2)
	
	for X_cur in range(flow_field.X_size):
		for Y_cur in range(flow_field.Y_size):
		
			img = font.render(str(flow_field.Cost.get(X_cur,Y_cur)), True, (255, 255, 255))
			
			#Draw the circle and blit the text onto the display
			pygame.draw.circle(gameDisplay, (min(flow_field.Integration.get(X_cur,Y_cur)*color_gain, 255), 50, 0), (int(X_cur*gain + x_offset), int(Y_cur*gain + y_offset)), 10)
			
			Next_X = flow_field.Flow.get(X_cur, Y_cur) % flow_field.Y_size
			Next_Y = flow_field.Y_size - Next_X
			
			gameDisplay.blit(img, (int(X_cur * gain + x_offset), int(Y_cur*gain + y_offset)))
			
	#Draw arrows ontop of everything else
	for X_cur in range(flow_field.X_size):
		for Y_cur in range(flow_field.Y_size):
		
			Next_X, Next_Y = flow_field.get_XY(flow_field.Flow.get(X_cur, Y_cur))
			
			pygame.draw.line(gameDisplay, (232, 3, 252), (int(X_cur*gain + x_offset), int(Y_cur*gain + y_offset)), (int(Next_X*gain + x_offset), int(Next_Y*gain + y_offset)))
			pygame.display.update()
			pygame.event.pump()
			time.sleep(0.10)
		
	#Update the display with the new images and clear the input
	while(True):
		pygame.event.pump()
	
#Create the field
field = Flow_Field(30,30, 4, 4)

#Configure the cost considerations
field.Cost.set(1,0,5)
field.Cost.set(2,0,5)
field.Cost.set(3,0,5)
field.Cost.set(4,0,5)
field.Cost.set(5,0,5)
field.Cost.set(6,0,5)
field.Cost.set(7,0,5)
field.Cost.set(8,0,5)
field.Cost.set(9,0,5)
field.Cost.set(4,3,5)
field.Cost.set(4,4,5)
field.Cost.set(4,5,5)
field.Cost.set(4,1,5)
field.Cost.set(4,2,5)
field.Cost.set(4,3,5)
field.Cost.set(4,4,5)
field.Cost.set(4,5,5)
field.Cost.set(4,6,5)
field.Cost.set(4,7,5)
field.Cost.set(4,8,5)
field.Cost.set(4,9,5)
field.Cost.set(4,10,5)
field.Cost.set(4,11,5)

field.Cost.set(9,3,5)
field.Cost.set(9,4,5)
field.Cost.set(9,5,5)
field.Cost.set(9,1,5)
field.Cost.set(9,2,5)
field.Cost.set(9,3,5)
field.Cost.set(9,4,5)
field.Cost.set(9,5,5)
field.Cost.set(9,6,5)
field.Cost.set(9,7,5)
field.Cost.set(9,8,5)
field.Cost.set(9,9,5)
field.Cost.set(9,10,5)
field.Cost.set(9,11,5)

field.Cost.set(8,11,5)
field.Cost.set(7,11,5)
field.Cost.set(6,11,5)
field.Cost.set(5,11,5)
field.Cost.set(4,11,5)


field.Cost.set(13, 13, 255)
field.Cost.set(13, 14, 255)
field.Cost.set(13, 15, 255)
field.Cost.set(13, 16, 255)
field.Cost.set(14, 16, 255)
field.Cost.set(15, 16, 255)
field.Cost.set(16, 16, 255)
field.Cost.set(16, 15, 255)
field.Cost.set(16, 14, 255)
field.Cost.set(15, 13, 255)
field.Cost.set(14, 13, 255)
field.Cost.set(13, 13, 255)



#Calculate the integration Field
start = time.time()
field.calc_integration()
print("Integratation took: " + str(time.time() - start) + " seconds")

#Calcuate the flow field
field.calc_flow()

#Display all the fields.
print(str(field.Cost))
print(str(field.Integration))
print(str(field.Flow))

pygame_flow_field_display(field)