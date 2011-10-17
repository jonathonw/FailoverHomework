import time
import sys

if __name__ == "__main__":
  if len(sys.argv) != 2 or float(sys.argv[1]) < 0 or float(sys.argv[1]) > 1:
    print "Usage:", sys.argv[0], "percentage"
    print "  where 'percentage' is a number between 0 and 1"
    exit(-1)
  
  percentage = float(sys.argv[1])
  
  if percentage == 0:
    exit(0)
  
  while True:
    result = 1
    for iteration in range(1, 100):
      result = result * iteration
      time.sleep(0.0001 - percentage/10000.0)
