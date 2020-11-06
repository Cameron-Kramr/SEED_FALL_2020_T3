####################Introduction####################
This is the readme for the code used in Demo 1. 
It directs the user on how to run the code as well as what each file does.


#################### Raspberry_Pi ####################
Main.py~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main code, implements connections and code flow

Comms/Pi_Comms_Multi_Threading.py~~~~~~~~~~~~~~~~~~~~ Serial and I2C communication thread definitions

Detection/Aruco_Multi_Threading.py~~~~~~~~~~~~~~~~~~~ Aruco marker detection and camera interface thread definitions
Detection/detect_angle.py~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Angle detection utility function definitions
Detection/filtering.py~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Filtering tests, not used

Navigation/pyflow.py~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Flow field class definition and example
Navigation/GPS/GPS.py~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GPS code for positioning using aruco markers
Navigation/GPS/Examples/kalman_filter.py~~~~~~~~~~~~~ Kalman filter example code
Navigation/GPS/Examples/kalman_filterpy_example.py~~~ Kalman filter using filterpy example code

#################### Control ####################

arduino/SerialCommMovement/SerialCommMovement.ino~~~~ Arduino code used for differental steering with serial comm inputs
arduino/Circles_example.ino~~~~~~~~~~~~~~~~~~~~~~~~~~ Arduino code used to test the rotational movement of the system
arduino/Test InstantVel.ino~~~~~~~~~~~~~~~~~~~~~~~~~~ Arduino code used to sample the velocity of both of the wheels 
arduino/Test_movementof#feet.ino~~~~~~~~~~~~~~~~~~~~~ Arduino code used to test the velocity control of the system in a straight line
arduino/Test_rotational_movement.ino~~~~~~~~~~~~~~~~~ Arduino code used to test the rotational velocity control of the system 

matlab/FixedSims_CorrectEdition.slx~~~~~~~~~~~~~~~~~~ Simulink model used to determine the velocity and positional controls for each of the wheels 
matlab/Matlab_Serial_Com_w_arduino.m~~~~~~~~~~~~~~~~~ Matlab code used to get sampled values for the velocity test
matlab/Workspace_FOr_test.mat~~~~~~~~~~~~~~~~~~~~~~~~ Matlab workspace values obtained from the velocity test
