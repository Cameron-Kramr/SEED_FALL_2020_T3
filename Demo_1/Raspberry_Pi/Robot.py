import multiprocessing
import time
import Navigation.GPS.GPS as GPS


class Robot:
	def __init__(self):
		self.GPS = GPS.GPS_System();
		
		self.Threads = []		#container for all threading objects generated
		self.Parameters = {}	#Dictionary for all parameters that will be used by updater functions
		
		