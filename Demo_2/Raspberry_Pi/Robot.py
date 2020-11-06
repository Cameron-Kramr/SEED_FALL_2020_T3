import multiprocessing as mp
import time
import Navigation.GPS.GPS as GPS
import enum

class Robot_States(enum.Enum):
    START_UP = 0 #State when robot starts up
    MOVE = 1     #State when robot is moving
    LOCATE = 2   #State when robot doesn't know where it is

class Robot:
	def __init__(self):
        self.Update_FPS = 60
        self.Start_Time = time.time()
        self.End_Time = time.time()

        self.GPS = GPS.GPS_System();

		self.Threads = {}		#container for all threading objects generated
		self.Parameters = {}	#Dictionary for all parameters that will be used by updater functions

        self.State = Robot_States.START_UP

    #Overridable initialization function to provide customization to code
    def initialize(self):
        #Initialize Aruco parameters
        cam_mtx = np.fromfile("Navigation/Camera_Utils/cam_mtx.dat").reshape((3,3))
        dist_mtx = np.fromfile("Navigation/Camera_Utils/dist_mtx.dat")
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_7X7_250)
        parameters = cv2.aruco.DetectorParameters_create()

    #Initiate Multiprocessing Pipes used for interconnecting the threads
        self.cv2_conn1, cv2_conn2 = mp.Pipe(duplex = True)
        self.pygme_conn1, pygme_conn2 = mp.Pipe(duplex = True)
        self.cv2_aruco_1_conn1, cv2_aruco_1_conn2 = mp.Pipe(duplex = True)
        self.cv2_aruco_2_conn1, cv2_aruco_2_conn2 = mp.Pipe(duplex = True)
        self.picam_conn1, picam_conn2 = mp.Pipe(duplex = True)
        self.I2C_pipe_1, I2C_pipe_2 = mp.Pipe(duplex = True)
        self.ARDU_pipe_1, ARDU_pipe_2 = mp.Pipe(duplex = True)

    #Create Multiprocessing Objects
        self.add_Thread("RASP_CAM", target = amt.picam_image_grabbler, args = (picam_conn2, [cv2_aruco_1_conn1, cv2_aruco_2_conn1], (640,480), 60,))
        self.add_Thread("PY_GAME", target = amt.pygame_aruco_display_manager, args = (pygme_conn2,))
        self.add_Thread("CV_DETECT_1", target = amt.cv2_detect_aruco_routine, args = (cv2_aruco_1_conn2, aruco_dict, parameters,))
        self.add_Thread("CV_DETECT_2", target = amt.cv2_detect_aruco_routine, args = (cv2_aruco_2_conn2, aruco_dict, parameters,))
        self.add_Thread("CV_POSE", target  = amt.cv2_estimate_pose, args = (cv2_conn2, 0.025, cam_mtx, dist_mtx, False, np.array([0,0,-0.0175]),))
        self.add_Thread("PI_I2C", target = pcmt.I2C_Handler, args = (I2C_pipe_2, (2,16), 0x08,))
        self.add_Thread("PI_ARDU", target = pcmt.Serial_Handler, args = (ARDU_pipe_2,))

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

################### Multi Threading Utilities
	def add_Thread(self, ID, target, args):
        self.Threads[ID] = mp.Process(target = target, args = args)

    def kill_Thread(self, ID):
        self.Threads[ID].kill()

    def kill_All_Threads(self):
        for i in self.Threads:
            i.kill()

    def close_Thread(self, ID):
            self.Threads[ID].close()

    def close_All_Threads(self, ID):
            for i in self.Threads:
                i.close()

    def start_Thread(self, ID):
        self.Threads[ID].start()

    def start_All_Threads(self):
            for i in self.Threads:
                i.start()
