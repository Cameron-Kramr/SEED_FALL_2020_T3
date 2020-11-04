import multiprocessing
import time


class Robot:
	__init__(self):
		self.Threads = []		#container for all threading objects generated
		self.Parameters = {}	#Dictionary for all parameters that will be used by updater functions