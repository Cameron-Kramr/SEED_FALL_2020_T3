from Modules.Module import module
import Modules.Movements as move

from collections import deque

class robot_control_handler(module):
    #initializer
    def __init__(self, args, ID = None):
        module.__init__(self, ID)
        args.State
        self.Movements = deque()
        self.Current_Movement = move.Movement()


    #Robot update routine. Defines behaviour of the robot
    def __update__(self, args):
        #print("Updating Robot Controller")
        if(self.Current_Movement != None):
            if(self.Current_Movement.check_Advance(args)): #Check advancement criteria
                print("Advancing Movement")
                if(len(self.Movements) != 0): #Get next movement if present
                    self.Current_Movement = self.Movements.popleft()
                else:   #Set current movement to none
                    self.Current_Movement = None
        elif(len(self.Movements) > 0): #Check if new movements present
            self.Current_Movement = self.Movements.popleft()

    #Adds a movement command to the que
    def add_move(self, movement):
        self.Movements.append(movement)
