import Module
from collections import deque

class I2C_Handler(Module.module):
    def __init__(self, args, pipe, ID = None):
        module.__init__(self, ID)
        self.Frame_Locked = True
        self.FPS = 0.7
        self.pipe = pipe
        
        args.I2C_MSSG = deque()

    def __update__(self, args):
        
        #Send off any arduino data that is present in the ARDU_Outgoing_Messages buffer deque
        try:
            if(args.I2C_MSSG != None):
                self.pipe.send(args.I2C_MSSG.popleft())
                args.I2C_MSSG = None
        except:
            args.I2C_MSSG = deque()
