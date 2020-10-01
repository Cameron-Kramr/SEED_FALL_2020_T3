import multiprocessing
import time

def spawn(num):
	for i in range(10):
		print(str(num) + " is on: " + str(i))
		time.sleep(0.25)

if __name__ == "__main__":
	for i in range(5):
		p = multiprocessing.Process(target = spawn, args=(i,))
		p.start()

