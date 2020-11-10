from GPS import GPS
from Modules.Module import module

class GPS_Handler(module):
    def __init__(self, args, raw_node_pipe, ID = -1):
        module.__init__(self, ID)

        args.GPS = GPS.GPS_System()

        self.raw_in = raw_node_pipe

    def __update__(self, args):
        while(self.raw_in.poll()):
            nodes = self.raw_in.recv()
            args.GPS.update(nodes)
            print("***GPS Position***")
            print(str(args.GPS.calc_node_Tw(nodes)))
