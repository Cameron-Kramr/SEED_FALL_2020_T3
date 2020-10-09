####################Introduction####################
This is the readme for the code used in the mini project demonstration. 
It directs the user on how to run the code as well as what each file does.

####################RPI CODE####################
MiniProj.py ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main python file. Run this to start RPI portion of code
Aruco_Multi_Threading.py ~~~~~~~~~~~~~~~~~ Functions for aruco detection
detect_angle.py ~~~~~~~~~~~~~~~~~~~~~~~~~~ Useful angle manipulation functions
Pi_Comms_Multi_Threading.py ~~~~~~~~~~~~~~ I2C communication functions
Examples/Calibration/mmal_calibrate.py ~~~ Calibration code for calibrating camera

rpi code not covered in this file is ansillary and not vital to operation or relevent to deliverables


####################Control####################
PIDControl/PIDControl.ino ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main code file for arduino. Upload this file to start arduino portion of code
motorEncoder.m ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Matlab Sript ran to compare experimental and simulated values found for the open loop system
Closed_OpenLoopedSystems.slx ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Simulink file containing both the closed loop and the open loop systems
step_response ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Arduino code used to test the motor angular velocity, and to determine the transfer funtion
closed loop/FixedPID(i think need to check with our motor) ~~ Arduino code used to compare the experimental values of the motor system with a PI controller 
closed loop/closedloopMatlab ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Matlab file used to compare experimental and simulated values found for the closed loop system
