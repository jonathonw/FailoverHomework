#!/usr/bin/env python

from twisted.protocols import basic
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet import error

from datetime import datetime

import sys
import os
import threading
import time

class NoLiveReplicasAvailableException(Exception):
  pass

class ClientProtocol(basic.LineReceiver):
  '''
  Receives lines from clients, then forwards them on to the message processor for
  processing (we don't do the processing in this class, because the processor
  maintains the system state needed to handle messages).
  '''
  
  def lineReceived(self, line):
    self._messageProcessor.processMessage(self, line)
    
  def sendMessage(self, msg):
    self.sendLine(msg)
    
  def connectionMade(self):
    self._messageProcessor = self.factory.messageProcessor
    
    if self.factory.onConnect != None:
      self.factory.onConnect(self)
      
  
  def connectionLost(self, reason):
    if self.factory.onDisconnect != None:
      self.factory.onDisconnect(self, reason)
      
    
      
class ClientMiddleware(threading.Thread):
  def __init__(self, faultManagerAddress, faultManagerPort, clientImplementation):
    threading.Thread.__init__(self)
    self._faultManagerAddress = faultManagerAddress
    self._faultManagerPort = faultManagerPort
    self._clientImplementation = clientImplementation
    self._replicaList = []
    self._faultManagerConnector = None
    self._faultManagerCondition = threading.Condition()
    self._operationArgument = None
    self._operationCompleteCondition = threading.Condition()
    self._operationResult = None
    
    self._replicaIndexToAttempt = 0
  
  def run(self):
    self._connectToFaultManager()
    reactor.run(False) #Argument False tells the reactor that it's not on the
                       #main thread, so it doesn't attempt to register signal
                       #handlers (which doesn't work on other threads)
    
  def _connectToFaultManager(self):
    factory = Factory()
    factory.protocol = ClientProtocol
    factory.messageProcessor = self
    factory.onConnect = self.connectedToFaultManager
    factory.onDisconnect = self.disconnectedFromFaultManager
    point = TCP4ClientEndpoint(reactor, self._faultManagerAddress, self._faultManagerPort)
    d = point.connect(factory)
    d.addErrback(self._onFaultManagerConnectError)
      
  def _onFaultManagerConnectError(self, e):
    e.printTraceback()
    reactor.stop()
    return e
  
  def connectedToFaultManager(self, connector):
    print "Connection to fault manager established."
    
    self._faultManagerCondition.acquire()
    self._faultManagerConnector = connector
    self._faultManagerCondition.notifyAll()
    self._faultManagerCondition.release()
    
    self._faultManagerConnector.sendLine("c") #inform the fault manager that we're a client
    
  def disconnectedFromFaultManager(self, connector, reason):
    if reactor.running:
      print "Fault manager disconnected (did it crash?)"
      if reason.check(error.ConnectionDone):
        print "Fault manager connection closed normally."
      else:
        print "Fault manager connection error..."
        reason.printTraceback()
      
      reactor.stop()
      
  def connectedToServerReplica(self, connector):
    operationMessage = "a," + str(self._operationArgument)
    print "Got a connection to a server replica. Sending command:", operationMessage
    connector.sendLine(operationMessage)
    
  def disconnectedFromServerReplica(self, connector, reason):
    if self._operationResult == None: #must not have gotten a result before disconnection; try the next replica
      self._connectToReplica()
    else:
      self._operationResult = None #now that we've disconnected, reset the result back to none
      
  def _onServerReplicaConnectError(self, e):
    self._connectToReplica()
    
  def processMessage(self, connector, msg):
    print "Client got message", msg
    operation = msg[0:1] #message type is the first character of the message
    if operation == "u":
      self._updateReplicaList(msg[2:]) #The replicaUpdate message accepts the rest of the payload as a string
    elif operation == "b":
      self._operationComplete(connector, msg[2:])  
    else:
      print "Unknown operation"
      
  def _updateReplicaList(self, newListMessage):
    if(newListMessage != ""):
      #make a list out of the string we received
      unprocessedReplicaList = newListMessage.split(",")
      #now break these up into (ip, port) pairs (where IP is a string, and port is an integer)
      self._replicaList = [ (address.split(":")[0], int(address.split(":")[1])) for address in unprocessedReplicaList]
    else:
      self._replicaList = []
    print "Got replicas:", self._replicaList
    self._replicaIndexToAttempt = 0
    
  def _connectToReplica(self):
    if self._replicaIndexToAttempt < len(self._replicaList):
      
      factory = Factory()
      factory.protocol = ClientProtocol
      factory.messageProcessor = self
      factory.onConnect = self.connectedToServerReplica
      factory.onDisconnect = self.disconnectedFromServerReplica
      
      (replicaAddress, replicaPort) = self._replicaList[self._replicaIndexToAttempt]
      print "Connecting to primary replica", replicaAddress + ":" + str(replicaPort)
      point = TCP4ClientEndpoint(reactor, replicaAddress, replicaPort)
      d = point.connect(factory)
      d.addErrback(self._onServerReplicaConnectError)
      self._replicaIndexToAttempt += 1
    else:
      #if we run out of replicas, send OperationComplete with result set to None
      #so that performOperation will raise an exception
      self._operationCompleteCondition.acquire()
      self._operationResult = None
      self._operationCompleteCondition.notifyAll()
      self._operationCompleteCondition.release()
    
  def _operationComplete(self, connector, resultMessage):
    self._operationCompleteCondition.acquire()
    connector.transport.loseConnection() #don't maintain active connections to servers
    self._operationResult = int(resultMessage)
    self._operationCompleteCondition.notifyAll()
    self._operationCompleteCondition.release()
    
  def waitForFaultManager(self):
    self._faultManagerCondition.acquire()
    if self._faultManagerConnector == None:
      self._faultManagerCondition.wait()
    self._faultManagerCondition.release()
    
  def performOperation(self, argument):
    self._operationArgument = argument
    
    reactor.callFromThread(self._connectToReplica)
    
    self._operationCompleteCondition.acquire()
    if self._operationResult == None:
      self._operationCompleteCondition.wait()
      
    #consume operation result and reset it back to None (so the next call won't
    #get the result from this iteration on failure)
    result = self._operationResult
    self._operationCompleteCondition.release()
    
    if result == None: #must have run out of replicas
      raise NoLiveReplicasAvailableException()
    
    return result
    
class Client:
  def __init__(self, faultManagerAddress, faultManagerPort):
    self._middleware = ClientMiddleware(faultManagerAddress, faultManagerPort, self)
  
  def run(self):
    self._middleware.start()
    self._middleware.waitForFaultManager()
    
    value = 0
    
    while True:
      time.sleep(5)
      print "Sending request to server..."
      try:
        startTime = time.clock()
        result = self._middleware.performOperation(value)
        stopTime = time.clock()
        computationTime = stopTime - startTime
        value = value + 1 #only incremented if we have a success; therefore, when coupled
                          #with properly performing replicas, result should always
                          #increment by one
        print "Got result:", result
        print "  Computation took", computationTime, "seconds"
      except NoLiveReplicasAvailableException:
        print "Couldn't connect to any active replicas..."
      
    
if __name__ == "__main__":
  if len(sys.argv) != 3:
    print "Usage:", sys.argv[0], "faultmgr-address faultmgr-port"
    exit(-1)
  
  try:
    client = Client(sys.argv[1], int(sys.argv[2]))
    client.run()
  except KeyboardInterrupt:
    print "Got ^C...  Closing"
    reactor.callFromThread(reactor.stop)
  except:
    print "Unexpected error...  dying."
    reactor.callFromThread(reactor.stop)
    raise
    
    
