import time
import sys
import threading

class BusyThread(threading.Thread):
  def __init__(self, percentage):
    threading.Thread.__init__(self)
    self._percentage = percentage
  
  def run(self):
    while True:
      result = 1
      for iteration in range(1, 100):
        for i in range(1, 20):
          result = result * iteration
        time.sleep(0.0005 - percentage*0.0005)

if __name__ == "__main__":
  if len(sys.argv) != 2 or float(sys.argv[1]) < 0 or float(sys.argv[1]) > 100:
    print "Usage:", sys.argv[0], "percentage"
    print "  where 'percentage' is a number between 0 and 100"
    exit(-1)
  
  percentage = float(sys.argv[1]) / 100.0
  
  if percentage == 0:
    exit(0)
  
  numberThreads = int(percentage * 10 + 1)
  
  for i in range(numberThreads):
    newThread = BusyThread(0.2)
    newThread.start()
    
  while True:
    time.sleep(1)
