import numpy as np
import time
from matplotlib import pyplot as plt

dt = 0.1
dt2 = dt **2
dt4 = dt **4

'''
Q = np.array([	dt4/4, 0, 0, 0, 0, 0,
				0, dt4/4, 0 ,0 ,0, 0,
				0, 0, dt4/4,0 ,0 ,0,
				0, 0, 0, dt2, 0, 0,
				0, 0, 0, 0, dt2, 0,
				0, 0, 0, 0, 0, dt2]).reshape((6,6))

'''
Q = np.array([	10, 0, 0, 0, 0, 0,
				0, 10, 0 ,0 ,0, 0,
				0, 0, 10,0 ,0 ,0,
				0, 0, 0, 10, 0, 0,
				0, 0, 0, 0, 10, 0,
				0, 0, 0, 0, 0, 10]).reshape((6,6))


R = np.array([	90, 0, 0, 0, 0, 0,
				0, 90, 0, 0, 0, 0,
				0, 0, 90, 0, 0, 0,
				0, 0, 0, 0.009, 0, 0,
				0, 0, 0, 0, 0.009, 0,
				0, 0, 0, 0, 0, 0.009]).reshape((6,6))

F = np.array([	1, 0, 0, dt, 0, 0,
				0, 1, 0, 0, dt, 0,
				0, 0, 1, 0, 0, dt,
				0, 0, 0, 1, 0, 0,
				0, 0, 0, 0, 1, 0,
				0, 0, 0, 0, 0, 1]).reshape((6,6))

B = np.array([	0.5*dt2, 0, 0,
				0, 0.5*dt2, 0,
				0, 0, 0.5*dt2,
				dt, 0, 0,
				0, dt, 0,
				0, 0, dt]).reshape((6,3))

H = np.identity(6)

uk0 = np.array([0, 10, 0])

P0p = np.array([16, 0, 0, 0, 0, 0,
				0, 16, 0, 0, 0, 0,
				0, 0, 16, 0, 0, 0,
				0, 0, 0, 0.16, 0, 0,
				0, 0, 0, 0, 0.16, 0,
				0, 0, 0, 0, 0, 0.16]).reshape((6,6))

x0p = np.array([2, -2, 0, 5, 5.1, 0.1])
zk = np.array([2, -2, 0, 5, 5.1, 0.1])

zk_rand = zk + np.random.normal(0, 1, 6)

xk1p = x0p
uk1 = uk0
Pk1p = P0p

loops = 100

xks = np.zeros((6,100))
zks = np.zeros((6,100))
zkrs = np.zeros((6,100))


for i in range(loops):
	#Prediction Stage
	xkm = F.dot(xk1p) + B.dot(uk1)
	Pkm = F.dot(Pk1p.dot(F.transpose())) + Q

	#Update:
	yk = zk_rand - xkm
	Kk = Pkm*H.transpose()*np.linalg.inv(R + Pkm)
	xkp = xkm + Kk.dot(yk)
	Pkp = (np.identity(6) - Kk*H)*Pkm

	#Prepare next stage:
	xks[:,i] = xkp
	xk1p = xkp
	Pklp = Pkp

	zks[:, i] = zk
	zkrs[:, i] = zk_rand

	zk  = F.dot(zk) + B.dot(uk1)
	
	zk_rand = zk + np.random.normal(0, 10, 6)
	
p1, = plt.plot(xks[1,:], label = "Xks")
p2, = plt.plot(zks[1,:], label = "Zks")
p3, = plt.plot(zkrs[1,:], label = "Zkrs")
plt.legend(handles=[p1, p2, p3])
plt.show()