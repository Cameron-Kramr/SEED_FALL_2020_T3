from Modules.Module import module
from collections import deque

class ARDU_Handler(module):
    def __init__(self, args, pipe, ID = None):
        module.__init__(self, ID)
        self.Frame_Locked = True
        self.FPS = 60
        self.pipe = pipe
        
        args.ARDU_Incoming_MSSG = deque()
        args.ARDU_Outgoing_MSSG = deque()
    
    
    def __update__(self, args):
        
        #Check for messages to receive
        '''while self.pipe.poll():
            try:
                args.ARDU_MSSG.append(self.pipe.recv())
            except:
                args.ARDU_Incoming_MSSG = deque()
                args.ARDU_Incoming_MSSG.append(self.pipe.recv())
        '''
        #Send off any arduino data that is present in the ARDU_Outgoing_Messages buffer deque
        try:
            while len(args.ARDU_Outgoing_MSSG) > 0:
                data = args.ARDU_Outgoing_MSSG.popleft()
                #print("~~~~~~~~~~~~~~~ Handler Sending Arduino: ~~~~~~~~~~~~~~~~")
                #print(data)
                self.pipe.send(data)
                #print("~~~~~~~~~~~~~~~ Handler Sent    Arduino: ~~~~~~~~~~~~~~~~")
        except:
            args.ARDU_Outgoing_MSSG = deque()
