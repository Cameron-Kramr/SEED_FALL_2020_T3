#Cameron Kramr
#11/06/2020
#EENG 350
#Section A
#Computer Vision
#NOTE, this module requires pygame to be installed in order to run
#This file implements the robot class which stores, and implements robot code

#Standard Modules
import sys
import numpy as np
import multiprocessing as mp
import math
import enum
import time
import Modules.Module

import Modules.GPS_Handler as gps
import Modules.Ardu_Handler as adh
import Modules.I2C_Handler as i2ch
import Modules.CV_Handler as cvh
import Modules.detect_angle as dta
import Modules.PyGame_Handler as pgh

import Threading.Pi_Comms_Multi_Threading as pcmt
import Threading.Aruco_Multi_Threading as amt

#Raspberry Pi Modules
import picamera
import cv2


class Robot_States(enum.Enum):
    START_UP = 0 #State when robot starts up
    MOVE = 1     #State when robot is moving
    SEARCH = 2   #Search for beacons state

###############     Robot Class Definition      ####################
class Robot():
    def __init__(self):
        self.Debug = False
        self.Update_FPS = 0
        self.Run_FPS = 0
        self.Start_Time = time.time()
        self.End_Time = time.time()

        self.Threads = {}        #container for all threading objects generated
        self.Modules = {}            #Dictionary for all pipes that will be used by updater functions
        self.State = Robot_States.START_UP

###################### Timing related functions ###################
    #Sets the start time
    def set_Start(self):
        self.Start_Time = time.time()

    #Sets the end time
    def set_End(self):
        self.End_Time = time.time()

    #Claculates the fps using the stored start and end times
    def calc_FPS(self):
        return 1/(self.End_Time - self.Start_Time)

    #Checks if time difference is greater than the update period
    def check_Time(self):
        return (1/self.Update_FPS >= self.End_Time - self.Start_Time)

    #Default Updater
    def update(self):
        if self.check_Time():
            print(self.calc_FPS())

################### Multi Threading Utilities #######################
    def add_Thread(self, ID, target, args):
        self.Threads[ID] = mp.Process(target = target, args = args)

    def kill_Thread(self, ID):
        self.Threads[ID].kill()

    def kill_All_Threads(self):
        for i in self.Threads:
            self.Threads[i].kill()

    def close_Thread(self, ID):
            self.Threads[ID].close()

    def close_All_Threads(self, ID):
            for i in self.Threads:
                self.Threads[i].close()

    def start_Thread(self, ID):
        self.Threads[ID].start()

    def start_All_Threads(self):
            for i in self.Threads:
                self.Threads[i].start()

######################### Updater Related Functions ###################

    #Updates all modules sending the robot handle for all global variables
    def update_Modules(self):
        self.set_Start()
        for i in self.Modules:
            #print("Updating: " + str(self.Modules[i].ID))
            self.Modules[i].update(self)
            #print(self.Modules[i].calc_FPS())
        self.set_End()
        self.Run_FPS = self.calc_FPS()
        if(self.Debug):
            print("Robot FPS: " + str(self.Run_FPS))
    #Updates a single module
    def update_Module(self, ID):
        self.Modules[ID].update(self)

    #Adds modules to the module list
    def add_Module(self, ID, module):
        self.Modules[ID] = module
        self.Modules[ID].ID = ID

    def debug_Module(self, ID):
        self.Modules[ID].Debug = True

    def debug_All_Modules(self):
        for i in self.Modules:
            self.debug_Module(i)

####################### Applicaiton specific robot derivative class ################################
class Demo_2_Robot(Robot):
    def __init__(self):
        Robot.__init__(self)
#Overridable initialization function to provide customization to code
        #Initialize Aruco parameters
        cam_mtx = np.fromfile("Modules/Camera_Utils/cam_mtx.dat").reshape((3,3))
        dist_mtx = np.fromfile("Modules/Camera_Utils/dist_mtx.dat")
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_7X7_250)
        parameters = cv2.aruco.DetectorParameters_create()

    #Initiate Multiprocessing Pipes used for interconnecting the threads
        cv2_conn1, cv2_conn2 = mp.Pipe(duplex = True)
        pygme_conn1, pygme_conn2 = mp.Pipe(duplex = True)
        pygme_local_1, pygme_local_2 = mp.Pipe(duplex = True)
        cv2_aruco_1_conn1, cv2_aruco_1_conn2 = mp.Pipe(duplex = True)
        cv2_aruco_2_conn1, cv2_aruco_2_conn2 = mp.Pipe(duplex = True)
        picam_conn1, picam_conn2 = mp.Pipe(duplex = True)
        I2C_pipe_1, I2C_pipe_2 = mp.Pipe(duplex = True)
        ARDU_pipe_1, ARDU_pipe_2 = mp.Pipe(duplex = True)
        GPS_Pipe_1, GPS_Pipe_2 = mp.Pipe(duplex = True)

    #Create Multiprocessing Objects
        self.add_Thread("RASP_CAM", target = amt.picam_image_grabbler, args = (picam_conn2, [cv2_aruco_1_conn1, cv2_aruco_2_conn1], (640,480), 60, False,))
        self.add_Thread("PY_GAME", target = amt.pygame_aruco_display_manager, args = (pygme_conn2,))
        self.add_Thread("CV_DETECT_1", target = amt.cv2_detect_aruco_routine, args = (cv2_aruco_1_conn2, aruco_dict, parameters,False,))
        self.add_Thread("CV_DETECT_2", target = amt.cv2_detect_aruco_routine, args = (cv2_aruco_2_conn2, aruco_dict, parameters, False,))
        self.add_Thread("CV_POSE", target  = amt.cv2_estimate_pose, args = (cv2_conn2, 0.025, cam_mtx, dist_mtx, False, np.array([0,0,-0.0175]),))
        self.add_Thread("PI_I2C", target = pcmt.I2C_Handler, args = (I2C_pipe_2, (2,16), 0x08,))
        self.add_Thread("PI_ARDU", target = pcmt.Serial_Handler, args = (ARDU_pipe_2,))

    #Create appropriate modules for handling thread interactions
        self.add_Module("PI_ARDU", adh.ARDU_Handler(self, ARDU_pipe_1))
        self.add_Module("PI_I2C", i2ch.I2C_Handler(self, I2C_pipe_1))
        self.add_Module("GPS", gps.GPS_Handler(self, GPS_Pipe_2))
        self.add_Module("PY_GAME", pgh.PyGame_Handler(self, pygme_local_2, pygme_conn1))

        side_length = 0.025
        offset_mat = np.array((0,0,0))

        self.add_Module("CV_POSE", cvh.CV_Handler(self, [cv2_aruco_1_conn1, cv2_aruco_2_conn1], cv2_conn1, [pygme_local_1, GPS_Pipe_1]))


if __name__ == "__main__":
    bob = Demo_2_Robot()
