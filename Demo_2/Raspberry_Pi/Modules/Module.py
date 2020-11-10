#Written by Cameron Kramr 11/6/2020
#Modules are used to handle main thread events for the robot class. This means any communication that might occur between pipes 

import time

#Module class handles frame locking and updating of individual modules on the robot
class module():
    def __init__(self, args, ID = None):
        #print("Module BOI")
        self.Frame_Locked = False
        self.FPS = 60
        self.Start_Time = time.time()
        self.End_Time = time.time()
        self.ID = ID
        self.Debug = False
        self.Active = True

    def set_Start(self):
        self.Start_Time = time.time()

    #Sets the end time
    def set_End(self):
        #print("End: " + str(self.End_Time))
        self.End_Time = time.time()

    #Claculates the fps using the stored start and end times
    def calc_FPS(self):
        #print("FPS: " + str(1/(self.End_Time - self.Start_Time)))
        return (1/(self.End_Time - self.Start_Time))

    #Checks if time difference is greater than the update period
    def check_Time(self):
        return (1/self.FPS <= self.End_Time - self.Start_Time)

    #Activate the module
    def activate(self):
        self.Active = True

    #Deactivate the module
    def deactivate(self):
        self.Active = False

    #Default Updater
    def __update__(self, args):
        print(str(self.ID) + " Module using default updater")

    #System updater function
    def update(self, args):
        self.set_End()
        if((not self.Frame_Locked or self.check_Time()) and self.Active):
            if(self.Frame_Locked and self.Debug):
                print(str(self.ID) + " at: " + str(self.calc_FPS()) + " FPS")
            self.set_Start()
            self.__update__(args)
            self.set_End()
        #else:
            #print("Not Updating")

if __name__ == "__main__":
    mod_1 = ARDU_Updater()

    #mod_1.__update__ = mod__update__
    mod_1.update("thisguy")
