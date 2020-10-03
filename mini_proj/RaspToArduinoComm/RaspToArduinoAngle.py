# Let me know if any questions come up.
# Also let me know if you want the version of this code that also displays the angles to
# the LCD Display.
# (Jesus Ramirez)
#------------------------------------------------

from smbus2 import SMBus
import time

bus = SMBus(1)
address = 0x08                          #has to be the same as the address in Arduino
angleRead = 90                          #variable to hold angle (degrees) read by computer vision
print("New ", angleRead)
data = (angleRead * 0.7)                #converts angle to a number between 0 and 252
data = int(round(data))                 #rounds the number to integer

bus.write_byte_data(address, 0, data)       #sends data to arduino (new position for wheel)

time.sleep(1)

data = bus.read_byte_data(address, 1)       #reads data sent from arduino (old wheel position)

data = data/0.7                         #converts data to degrees
print("Old ", data)

bus.close()







