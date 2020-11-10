from Modules.Module import module
from enum import intEnum
from collections import deque

class robot_states(enum.intEnum):
    SEARCH = 1


class robot_control_handler(module):
    #initializer
    def __init__(self, args):
        args.State

    #Robot update routine. Defines behaviour of the robot
    def __update__(self, args):
        if(self.State == robot_states.SEARCH):
            pass

    #Sends command to arduino
    def send_ardu_cmd(self, args, cmd):
        try:
            args.ARDU_Outgoing_MSSG.append(cmd)
        except:
            args.ARDU_Outgoing_MSSG = deque()
            args.ARDU_Outgoing_MSSG.append(cmd)

    #Search for nodes
    def search(self, args, target = -1):
        if(target in args.Recent_Marers):
            #Stop looking
            pass
        else:

    #Goes to a position in space
    def go_to(self, args, pos):
