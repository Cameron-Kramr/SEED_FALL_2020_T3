from filterpy.kalman import kalmanFilter

f = KalmanFilter(dim_x =2, dim_z=1)

#Assign the initial value for the state
f.x = np.array([[2.], # Position
				[0.]]) # Velocity

#Define the state transition matrix
f.F = np.array([[1.,1.],[0.,1.]])

#Define the measurement function
f.H = np.array([[1.,0.]])

#Define covariance matrix
f.P = np.array([[1000., 0.],
				[0., 	1000.]])

#Assign measurement noise (dimension is 1x1 so scalar is good enough)
f.R = np.array([[5.]])

#Process noise variable
from filterpy.common import Q_discrete_white_noise
f.Q = Q_discrete_white_noise(dim=2, dt=0.1, var = 0.13)

z = get_sensor_reading()
f.predict()
f.update(z)

do_something_with_estimate(f.x)
