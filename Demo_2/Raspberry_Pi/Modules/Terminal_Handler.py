import curses
from Modules.Module import module

__ch_set = ['\n']
old_settings=None

def init_anykey():
   global old_settings
   old_settings = termios.tcgetattr(sys.stdin)
   new_settings = termios.tcgetattr(sys.stdin)
   new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON) # lflags
   new_settings[6][termios.VMIN] = 0  # cc
   new_settings[6][termios.VTIME] = 0 # cc
   termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)

def Get_Line():
    ch = os.read(sys.stdin.fileno(), 1)
    #print('>', end = '')
    if(len(__ch_set) != 0):
       if(__ch_set[-1] == '\n' or __ch_set[-1] == '\r'):
            __ch_set.clear()

    while ch != None and len(ch) > 0:
        __ch_set.append(chr(ch[0]))
        #print(chr(ch[0]), end = '')
        if(chr(ch[0]) == '\r' or chr(ch[0]) == '\n'):
            return __ch_set
        ch = os.read(sys.stdin.fileno(), 1)
    return None;

#Terminal handler for handling terminal events like keyboard presses
class Terminal_Handler(module):
    def __init__(self, ID = None):
        module.__init__(self, ID = ID)
