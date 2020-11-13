from GPS import GPS 
from Modules.Module import module

class GPS_Handler(module):
    def __init__(self, args, raw_node_pipe, ID = -1):
        module.__init__(self, ID)

        args.GPS = GPS.GPS_System()
        args.Position = [0,0,0]
        self.raw_in = raw_node_pipe
        self.Frame_Locked = True
        self.FPS = 100

    def __update__(self, args):
        count = 0
        while(self.raw_in.poll()):
            #self.set_Start()
            nodes = self.raw_in.recv()
            #self.set_Start()
            args.GPS.update(nodes)
            #print("***GPS Position***")
            args.Position = args.GPS.calc_node_Tw(nodes).reshape(3)
            #print(args.Position)
            #self.set_End()
            #print("FPS: " + str(self.calc_FPS()))
            #count += 1
        #print("Looked at: " + str(count) + " markers")
