#Vector Flow Path finding
#Written By: Cameron Kramr
#Date: 08/25/2020
#EENG 350
#References:http://leifnode.com/2013/12/flow-field-pathfinding/
#https://gamedevelopment.tutsplus.com/tutorials/understanding-goal-based-vector-field-pathfinding--gamedev-9007
#http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter23_Crowd_Pathfinding_and_Steering_Using_Flow_Field_Tiles.pdf
#https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

#This code generates a vector field based on cost that can be used for navigation. To use it, simply run the code. If you want to
#Change the path, edit the cost field as is done below. Changing these values will cause the vector field to be different and
#So make a different path. This code generates the shortest path toward the goal for every possible starting position.
#The results can be verified in the output by looking at the second graph which shows the Integration function. 
#If you start at any point on this plot, following the neighbour with the lowest value will lead to the goal (default (0,0)).
#The last graph shows the node that each node leads to. These are done by ID and so can be difficult to follow.
#This algorithm can be slow for large areas

from array import array
import sys
import math
import time

#Field container for field operations
class Field:

    #Class initializer creates variables used later
    def __init__(self, X_size = 1, Y_size = 1, type = 'i', default_value = 0):

        self.Field = array(type, [default_value for i in range(X_size * Y_size)] )
        
        self.X_size = X_size
        self.Y_size = Y_size

    #String override used to print out fields to console
    def __str__(self):
        output = ""
        #Iterate over every element
        for i in range(self.X_size):
            for j in range(self.Y_size):
                output += str(round(self.get(i,j), 3)) + '\t' #Convert each value to string
            output += '\n' #return carriage evertime we need it
        return output

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
    #Selected field consists of 0's for unselected/visited nodes and 1's for visited nodes
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
    def __init__(self, X_size = 1, Y_size = 1, goal_x = 0, goal_y = 0):
        self.Cost         =   Field(X_size, Y_size, 'f', 1)
        self.Integration  =   Field(X_size, Y_size, 'f', 0)
        self.Flow         =   Field(X_size, Y_size, 'I', 0)
        
        self.X_size = X_size
        self.Y_size = Y_size

        self.X_goal = goal_x
        self.Y_goal = goal_y

    #Calculates the integration value using a slight variation of Dijkstra's algorithm to 
    #Find the path cost of every element in the array to the goal
    def calc_integration(self):
        #Visited list keeps track of which nodes have been visited
        visited = Field(self.X_size, self.Y_size, 'B', 0)
        
        #Set the Integration list to max just like 
        self.Integration.set_all(sys.float_info.max)
        self.Integration.set(self.X_goal, self.Y_goal, 0)

        #First value is the goal with a distance of 0
        X_cur = self.X_goal
        Y_cur = self.Y_goal
        Dist_cur = 0

        for i in visited.Field:
            
            #X stationary Y plus 1 case
            if(Y_cur < self.Y_size - 1):
                working = self.Cost.get(X_cur, Y_cur + 1) + 1 + Dist_cur    #Calculates the path cost from the goal to this node
                if(working <= self.Integration.get(X_cur, Y_cur + 1) and visited.get(X_cur, Y_cur + 1) != 1):   #If this path to the node is less than the other
                    self.Integration.set(X_cur, Y_cur + 1, working) #Set the new Integration path cost to the smaller value
            
            #X stationary Y minus 1 case
            if(Y_cur != 0):
                working = self.Cost.get(X_cur, Y_cur - 1) + 1 + Dist_cur
                if(working <= self.Integration.get(X_cur, Y_cur - 1) and visited.get(X_cur, Y_cur - 1) != 1):
                    self.Integration.set(X_cur, Y_cur - 1, working)

            #Y Stationary X plus 1 case
            if(X_cur < self.Y_size - 1): 
                working = self.Cost.get(X_cur + 1, Y_cur) + 1 + Dist_cur
                if(working <= self.Integration.get(X_cur + 1, Y_cur) and visited.get(X_cur + 1, Y_cur) != 1):
                    self.Integration.set(X_cur + 1, Y_cur, working)
            
            #Y Stationary X minus 1 case
            if(X_cur != 0): 
                working = self.Cost.get(X_cur - 1, Y_cur) + 1 + Dist_cur
                if(working <= self.Integration.get(X_cur - 1, Y_cur) and visited.get(X_cur - 1, Y_cur) != 1):
                    self.Integration.set(X_cur - 1, Y_cur, working)
            
            #X Plus 1 Y Plus 1 case
            if(X_cur < self.X_size - 1 and Y_cur < self.Y_size - 1):
                working = self.Cost.get(X_cur + 1, Y_cur + 1) + math.sqrt(2) + Dist_cur
                if(working <= self.Integration.get(X_cur + 1, Y_cur + 1) and visited.get(X_cur + 1, Y_cur + 1) != 1):
                    self.Integration.set(X_cur + 1, Y_cur + 1, working)

            #X minus 1 Y minus 1 case
            if(X_cur != 0 and Y_cur != 0):
                working = self.Cost.get(X_cur - 1, Y_cur - 1) + math.sqrt(2) + Dist_cur
                if(working <= self.Integration.get(X_cur - 1, Y_cur - 1) and visited.get(X_cur - 1, Y_cur - 1) != 1):
                    self.Integration.set(X_cur - 1, Y_cur - 1, working)
            
            #X Plus 1 Y minus 1 case
            if(X_cur < self.X_size - 1 and Y_cur != 0):
                working = self.Cost.get(X_cur + 1, Y_cur - 1) + math.sqrt(2) + Dist_cur
                if(working <= self.Integration.get(X_cur + 1, Y_cur - 1) and visited.get(X_cur + 1, Y_cur - 1) != 1):
                    self.Integration.set(X_cur + 1, Y_cur - 1, working)
            
            #X Minus 1 Y Plus 1 case
            if(Y_cur < self.Y_size - 1 and X_cur != 0):
                working = self.Cost.get(X_cur - 1, Y_cur + 1) + math.sqrt(2) + Dist_cur
                if(working <= self.Integration.get(X_cur - 1, Y_cur + 1) and visited.get(X_cur - 1, Y_cur + 1) != 1):
                    self.Integration.set(X_cur - 1, Y_cur + 1, working)

            visited.set(X_cur, Y_cur, 1)
            [X_cur, Y_cur] = self.Integration.find_smallest_not_selected(visited)
            Dist_cur = self.Integration.get(X_cur, Y_cur)
            
    #Populates the flow field where each node points to the absolute position of the neighboring node with the shortest path length
    def calc_flow(self):
        for X_cur in range(self.X_size):
            for Y_cur in range(self.Y_size):
                smallest = sys.float_info.max
                Direction = 0

                    #X stationary Y plus 1 case
                if(Y_cur < self.Y_size - 1):
                    working = self.Integration.get(X_cur, Y_cur + 1) #Finds the neighbour's path cost
                    if(working <= smallest):    #Compares neightbour's path cost to smallest
                        smallest = working  #Sets new smallest
                        self.Flow.set(X_cur, Y_cur, X_cur + (Y_cur + 1)*self.Y_size) #Store the location in the field array of the neighbour
                
                #X stationary Y minus 1 case
                if(Y_cur != 0):
                    working = self.Integration.get(X_cur, Y_cur - 1)
                    if(working <= smallest):
                        smallest = working
                        self.Flow.set(X_cur, Y_cur, X_cur + (Y_cur - 1)*self.Y_size)

                #Y Stationary X plus 1 case
                if(X_cur < self.Y_size - 1): 
                    working = self.Integration.get(X_cur + 1, Y_cur)
                    if(working <= smallest):
                        smallest = working
                        self.Flow.set(X_cur, Y_cur, X_cur + 1 + (Y_cur)*self.Y_size)
                
                #Y Stationary X minus 1 case
                if(X_cur != 0): 
                    working = self.Integration.get(X_cur - 1, Y_cur)
                    if(working <= smallest):
                        smallest = working
                        self.Flow.set(X_cur, Y_cur, X_cur - 1 + (Y_cur)*self.Y_size)
                
                #X Plus 1 Y Plus 1 case
                if(X_cur < self.X_size - 1 and Y_cur < self.Y_size - 1):
                    working = self.Integration.get(X_cur + 1, Y_cur + 1)
                    if(working <= smallest):
                        smallest = working
                        self.Flow.set(X_cur, Y_cur, X_cur + 1 + (Y_cur + 1)*self.Y_size)

                #X minus 1 Y minus 1 case
                if(X_cur != 0 and Y_cur != 0):
                    working = self.Integration.get(X_cur - 1, Y_cur - 1)
                    if(working <= smallest):
                        smallest = working
                        self.Flow.set(X_cur, Y_cur, X_cur - 1 + (Y_cur - 1)*self.Y_size)
                
                #X Plus 1 Y minus 1 case
                if(X_cur < self.X_size - 1 and Y_cur != 0):
                    working = self.Integration.get(X_cur + 1, Y_cur - 1)
                    if(working <= smallest):
                        smallest = working
                        self.Flow.set(X_cur, Y_cur, X_cur + 1 + (Y_cur - 1)*self.Y_size)
                
                #X Minus 1 Y Plus 1 case
                if(Y_cur < self.Y_size - 1 and X_cur != 0):
                    working = self.Integration.get(X_cur - 1, Y_cur + 1)
                    if(working <= smallest):
                        smallest = working
                        self.Flow.set(X_cur, Y_cur, X_cur - 1 + (Y_cur + 1)*self.Y_size)
            

    def calc_move_vec(self, X_start, Y_start):
        next = self.Flow.get(X_start, Y_start)
        X_next = next % self.X_size
        Y_Next = next - X_next * self.X_size

        return [X_next, Y_next]

    def render_flow(self):
        for i in self.Flow:
            return 0

#Create the field
field = Flow_Field(150,15)

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