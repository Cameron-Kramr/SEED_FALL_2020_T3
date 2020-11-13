import numpy as np
import time
import math

from Threading.Pi_Comms_Multi_Threading import ARDU_CMD
from Threading.Pi_Comms_Multi_Threading import I2C_CMD

#Default movement class declaration
class Movement():
    def __init__(self, args = None, cmd = None, locked = False, fps = 100):
        self.cmd = cmd
        self.Frame_Locked = locked
        self.FPS = fps
        self.Start_Time = time.time()
        self.End_Time = time.time()

    #Default value is to advance to next movement
    def check_Advance(self, args):
        return True

    #Sends a command into the arduino command pipeline
    def send_cmd(self, args):
        #print(self.cmd)
        if(self.cmd != None):
            args.ARDU_Outgoing_MSSG.append(self.cmd)

    def set_Start(self, start = None):
        if(start == None):
            self.Start_Time = time.time()
        else:
            self.Start_Time = time.time()

    def set_End(self, end = None):
        if(end == None):
            self.End_Time = time.time()
        else:
            self.End_Time = end

    def check_Time(self):
        return (self.Start_Time >= self.End_Time)

    #Check the FPS
    def check_FPS(self):
        return (1/self.FPS <= self.End_Time - self.Start_Time)

    def calc_FPS(self):
        return 1/(self.End_Time - self.Start_Time)


#Simple movement command used
class Move(Movement):
    def __init__(self, args, vel, omega, rad, time = -1, blocking = True):
        Movement.__init__(self, args, [ARDU_CMD.SEND, "V" + str(vel) + " O" + str(omega) + " R" + str(rad) + " T" + str(time)])
        self.time_out = time
        self.End = None
        self.blocking = blocking

    def check_Advance(self, args):
        if(self.End == None):
            self.send_cmd(args)
            self.End = time.time() + self.time_out
            args.I2C_MSSG.append([I2C_CMD.SET_CLR, (255,0,0)])
            print("Starting Movement")


        #If time_out is default (-1) End was set in the past
        if(not self.blocking or self.End <= time.time()):
            args.I2C_MSSG.append([I2C_CMD.SET_CLR, (0,255,0)])
            return True
        else:
            time_rat = (self.End - time.time())/self.time_out
            #print(int((1-time_rat)*255))
            args.I2C_MSSG.append([I2C_CMD.SET_CLR, (min(255, int(255*abs(time_rat))),min(int(255*abs(1 - time_rat)), 255),0)])
            return False

#Scans area for markers, target is optional
class Scan_Marker(Movement):
    def __init__(self, args, omega, rot_time, time_out, target = -1):
        Movement.__init__(self, args)
        self.End_Time = None
        self.End = None
        self.time_out = time_out
        self.target = target
        self.rot_time = rot_time
        self.omega = omega
        self.rotating = True

    #Scan checks to see if a target node has been seen or if the timeout has occurred
    def check_Advance(self, args):
        #print("Checking markers")
        if(self.End_Time == None):
            self.cmd = [ARDU_CMD.SEND, "O" + str(self.omega) + " T" + str(self.rot_time)]
            self.send_cmd(args)
            print("Looking for " + str(self.target))
            self.End = time.time() + self.time_out
            self.set_Start()
            self.set_End(time.time() + self.rot_time)
        if(self.target in args.Recent_Markers or time.time() >= self.End):
            self.cmd = [ARDU_CMD.SEND, "O0"]
            self.send_cmd(args)
            print("Found Marker: " + str(self.target))
            return True
        elif(self.check_Time() and self.rotating):
            print("Done Rotating")
            self.cmd = [ARDU_CMD.SEND, "O0"]
            self.send_cmd(args)
            self.set_End(time.time() + self.rot_time*2)
            self.rotating = False
        elif(self.check_Time() and not self.rotating):
            print("Starting Rotations")
            self.cmd = [ARDU_CMD.SEND, "O" + str(self.omega) + " T" + str(self.rot_time)]
            self.send_cmd(args)
            self.set_End(time.time() + self.rot_time)
            self.rotating = True
        self.set_Start()
        return False

#Movement command that looks at a marker
class Point_at_Marker(Movement):
    def __init__(self, args, target, threshold, rate = 0.01, default = 1, locked = True, fps = 25):
        Movement.__init__(self, args, locked = locked, fps = fps)
        self.target = target
        self.threshold = threshold
        self.rate = rate
        self.cmd = None
        self.Default_Omega = default
        #args.I2C_MSSG.append([I2C_CMD.LCD_CLR_MSG, "Pointing at: " + str(self.target)])


    #Claculates the omega based on where the marker is relative to the robot
    def calc_omega(self, args):
        angle = None
        for i in args.Recent_Pose:
            #print(i[0])
            if i[0] == self.target:
                angle = math.atan2(i[1][0], i[1][2]) # - math.pi/2
                #print("i is at: " + str(angle/math.pi*180))
                return angle*self.rate
        return None

    #Checks if code is ready to go to next stage
    def check_Advance(self, args):
        omega = self.calc_omega(args)
        if(omega != None):
            if(abs(omega/self.rate) <= self.threshold):
                #Stop moving
                args.I2C_MSSG.append([I2C_CMD.SET_CLR, (0,255,0)])
                self.cmd = [ARDU_CMD.SEND, "O0\n"]
                self.send_cmd(args)
                print("Within Range")
                return True
        else:
            omega = self.Default_Omega
        if(self.check_FPS()):
            self.set_Start()
            omega_rat = omega/(self.rate*math.pi)
            args.I2C_MSSG.append([I2C_CMD.SET_CLR, (min(255, 255*(abs(omega_rat))) ,min(255, 255*(abs((1-omega_rat)))),0)])
            print(omega*180/math.pi)
            self.cmd = [ARDU_CMD.SEND, " O" + str(omega) + " V0 R0"]
            self.send_cmd(args)
            self.set_End()
            return False
        self.set_End()

class Stop_Robot(Movement):

    def check_Advance(self, args):
        self.cmd = [ARDU_CMD.SEND, " O0 V0 R0"]
        self.send_cmd(args)
        args.Continue = False
        return True


class Move_To_Target(Movement):
    def __init__(self, args, target, dist_to, threshold = 0.01, rate = 0.01, locked = True, fps = 12):
        Movement.__init__(self,args)
        self.target = target
        self.dist_to = dist_to
        self.threshold = threshold
        self.rate = rate

    def get_distance(self, args):
        position = args.Position
        target = args.GPS.Tw[:, args.GPS.Nodes[self.target]]
        #print(position - target)

        difference = position - target

        return math.sqrt(difference[0]**2 + difference[2]**2)

    def check_Advance(self,args):
        distance = self.get_distance(args)
        vel = (distance - self.dist_to)*self.rate
        if(abs(distance - self.dist_to) <= (self.threshold) and self.check_FPS()):
            print("dist sending cmd")
            self.set_Start()
            self.cmd = [ARDU_CMD.SEND, "V0"]
            self.send_cmd(args)
            self.set_End()
            print("Within distance")
            return  True
        elif(self.check_FPS()):
            print("Distance: " + str(distance))
            self.set_Start()
            self.cmd = [ARDU_CMD.SEND, "V" + str(vel) + " R0 O0"]
            self.send_cmd(args)
            return False
        self.set_End()


class Move_To_Target_Dumb(Movement):
    def __init__(self, args, target, dist_to, speed):
        Movement.__init__(self,args)
        self.target = target
        self.dist_to = dist_to
        self.speed = speed
        self.duration = None

    def get_distance(self, args):
        position = args.Position
        target = args.GPS.Tw[:, args.GPS.Nodes[self.target]]
        #print(position - target)

        difference = position - target

        return math.sqrt(difference[0]**2 + difference[2]**2)

    def check_Advance(self,args):
        self.set_Start()

        if(self.duration == None):
            distance = self.get_distance(args) - self.dist_to
            self.duration = distance/self.speed
            self.set_End(time.time() + self.duration)
            print("Distance: " + str(distance))
            print("Time: " + str(self.duration))
            self.cmd = [ARDU_CMD.SEND, "V" + str(self.speed) + " T" + str(self.duration) + " R0 O0"]
            self.send_cmd(args)
        elif(self.check_Time()):
            self.cmd = [ARDU_CMD.SEND, "V0"]
            self.send_cmd(args)
            print("Within distance")
            return  True
        else:
            return False

