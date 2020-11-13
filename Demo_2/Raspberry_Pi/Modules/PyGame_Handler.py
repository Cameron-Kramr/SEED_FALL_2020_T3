from Modules.Module import module

class PyGame_Handler(module):
    def __init__(self, args, input_pipe, output_pipe, ID = None):
        module.__init__(self, args, ID)
        self.Frame_Locked = True
        self.FPS = 30
        self.output = output_pipe
        self.input = input_pipe

    def __update__(self,args):
        if(self.input.poll()):
            #Get latest data
            while(self.input.poll()):
                data = self.input.recv()

            output = []

            for i in args.GPS.Nodes:
                output.append([i, args.GPS.Tw[:, args.GPS.Nodes[i]].reshape(3)])
            output.append(["ROB", args.Position.reshape(3)])
            self.output.send(output)
