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