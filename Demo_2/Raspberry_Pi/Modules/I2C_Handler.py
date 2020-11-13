from Modules.Module import module
from collections import deque

class I2C_Handler(module):
    def __init__(self, args, pipe, ID = None):
        module.__init__(self, ID)
        self.Frame_Locked = True
        self.FPS = 1
        self.pipe = pipe
        
        args.I2C_MSSG = deque()

    def __update__(self, args):
        
        #Send off any arduino data that is present in the ARDU_Outgoing_Messages buffer deque
        try:
            if(len(args.I2C_MSSG) != 0):
                #print("Sending Pipe: " + args.I2C_MSSG)
                while(len(args.I2C_MSSG)):
                    msg = args.I2C_MSSG.popleft()
                self.pipe.send(msg)
        except:
            args.I2C_MSSG = deque()
