import os
import sys
import time

def getCpu():
  #Format of CPU line in /proc/stat is:
  #   user nice system idle
  #This function returns: (usage, total) = (user + nice + system, user + nice + system + idle).
  #Basically, a pair of values representing a sample of CPU utilization.
  #If we sleep between calls, we can subtract these values and get an average
  #CPU percentage over that span of time.
  
  f = open('/proc/stat', 'r')
  cpuLine = f.readline() #assume that CPU line is the first line (it is in every implementation I've seen)
  f.close()
  cpuValues = cpuLine.split()
  print cpuValues
  user = int(cpuValues[1])
  nice = int(cpuValues[2])
  system = int(cpuValues[3])
  idle = int(cpuValues[4])
  
  print user, nice, system, idle
  
  usage = user + nice + system
  total = usage + idle
  
  return (usage, total) 
  

if __name__ == "__main__":
  (usage1, total1) = getCpu()
  time.sleep(1)
  (usage2, total2) = getCpu()
  print "Percent utilization:", float(usage2 - usage1) / float(total2 - total1)
