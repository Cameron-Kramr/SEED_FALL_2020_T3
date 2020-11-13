#Cameron Kramr 11/06/2020 EENG 350 Section A Computer Vision NOTE, this 
#module requires pygame to be installed in order to run This file ties 
#together all the project files and implements the program structure

#System Imports
import sys
import numpy as np
import time
import math

import Modules.Movements as move

#Custom Library Imports
#import Detection.detect_angle as dta
import Robot

#import Modules.GPS_Handler



robot = Robot.Demo_2_Robot()
#robot.Debug = True

Cont = "Robot_Ctrl"

robot.Modules[Cont].add_move(move.Move(robot, 0, 0, 0, 3))
#robot.Modules[Cont].add_move(move.Move(robot, 0, 1.25, 1, 5))
#robot.Modules[Cont].add_move(move.Move(robot, 0, 0, 0))
robot.Modules[Cont].add_move(move.Scan_Marker(robot, 0.5, 1, 20))
robot.Modules[Cont].add_move(move.Point_at_Marker(robot, 0, 0.01, rate = -0.5, default = 0.25))
#robot.Modules[Cont].add_move(move.Move(robot, 0, 0, 0, 3))
#robot.Modules[Cont].add_move(move.Point_at_Marker(robot, 0, 0.01, rate = -0.25, default = 0.25))
robot.Modules[Cont].add_move(move.Move(robot, 0, 0, 0, 6))
#robot.Modules[Cont].add_move(move.Move(robot, 1, 0, 0, 3))
robot.Modules[Cont].add_move(move.Move_To_Target_Dumb(robot, 0, 0.4, speed = 0.3048))
robot.Modules[Cont].add_move(move.Move(robot, 0, 0, 0, 3))
robot.Modules[Cont].add_move(move.Move(robot, 0, 1.5, 0, 1.3))
robot.Modules[Cont].add_move(move.Move(robot, 0, -1.25, 1, 5.59))
robot.Modules[Cont].add_move(move.Stop_Robot())

robot.start_All_Threads()

#robot.debug_All_Modules()

while(robot.Continue):
    robot.update_Modules()

robot.kill_All_Threads()
