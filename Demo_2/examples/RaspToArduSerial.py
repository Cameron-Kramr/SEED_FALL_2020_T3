import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600)             #Its either ACM0 or ACM1, it changes between the two when the arduino is plugged in using the USB cable.

time.sleep(2)                                         #gives it time to set up ser

for data in [6, 150, 168,540,1001, 54, 9]:            #arbitrary list of integers
  ser.write(data.to_bytes(2, 'big')                   #converts integer to bytes and sends them to arduino
  data2 = ser.readline().decode('utf-8').rstrip()     #reads the first "Serial.println()" the arduino sends
  print(data2)                                        #prints the data sent from arduino

#
