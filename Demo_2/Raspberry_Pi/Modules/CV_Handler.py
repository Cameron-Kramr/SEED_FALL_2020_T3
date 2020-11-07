import Module
import numpy as np
import cv2

class CV_Handler(Module.module):
    def __init__(self, args, cv_pipes, receiving_pipes, side_length, cam_mtx, dis_coefs, offset_mat = np.zeros((3))), ID = None):
        module.__init__(self, ID)
        self.Frame_Locked = False

        self.cv_pipes = cv_pipes
        self.receiving_pipes = receiving_pipes
        
        self.side_length = side_length
        self.cam_mtx = cam_mtx
        self.dis_coefs = dis_coefs
        self.offset_mat = offset_mat

    def __update__(self, args):
        
        #check all input pipes and send any present data to all the output pipes
        output = []
        input = []
        
        for cv_pipe in cv_pipes:
            while cv_pipe.poll:
                #Check if data is present
                
                #Expect data of shape:
                #([id, corners], ...)
                #blocking wait on data to appear at input pipe                
                data = cv_pipe.recv()
                    
                #Loop over the inputs received from the pipe
                for i in data:
                    #Find the translation and rotation vectors. Object points less important
                    rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(i[1], self.side_length, self.cam_mtx, self.dis_coefs)
                    #Offset can be used to set the center position of the marker within itself, if it is in a cube for example
                    
                    dst, _ = cv2.Rodrigues(rvecs)

                    tvecs = tvecs + dst@offset_mat
                    output.append([i[0], rvecs, tvecs])
                    
        if(len(output) != 0):
            #Send present data to receiver pipes
            for receiver in receiving_pipes:
                receiver.send(output)