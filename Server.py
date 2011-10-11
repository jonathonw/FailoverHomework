#!/usr/bin/env python

from twisted.protocols import basic
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet import error

from datetime import datetime

import sys
import os

class ServerProtocol(basic.LineReceiver):
  '''
  Receives lines from clients, then forwards them on to the Fault Manager for
  processing (we don't do the processing in this class, because the Fault
  Manager maintains the system state needed to handle messages).
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
      
    
      
class ServerMiddleware:
  def __init__(self, localAddress, localPort, faultManagerAddress, faultManagerPort, serverImplementation):
    self._localAddress = localAddress
    self._localPort = localPort
    self._faultManagerAddress = faultManagerAddress
    self._faultManagerPort = faultManagerPort
    self._serverImplementation = serverImplementation
    self._state = self._serverImplementation.getInitialState()
    self._replicaList = []
    self._faultManagerConnector = None
  
  def run(self):
    self._listen()
    #set up periodical load average updates to fault manager
    self._connectToFaultManager()
    reactor.run()
    
  def _listen(self):
    factory = Factory()
    factory.protocol = ServerProtocol
    factory.messageProcessor = self
    factory.onConnect = self.clientConnected
    factory.onDisconnect = self.clientDisconnected
    point = TCP4ServerEndpoint(reactor, self._localPort)
    d = point.listen(factory)
    d.addErrback(self._onListenError)
    
  def _connectToFaultManager(self):
    factory = Factory()
    factory.protocol = ServerProtocol
    factory.messageProcessor = self
    factory.onConnect = self.connectedToFaultManager
    factory.onDisconnect = self.disconnectedFromFaultManager
    point = TCP4ClientEndpoint(reactor, self._faultManagerAddress, self._faultManagerPort)
    d = point.connect(factory)
    d.addErrback(self._onListenError)
      
  def _onListenError(self, e):
    e.printTraceback()
    reactor.stop()
    return e
    
  def clientConnected(self, client):
    print "Connection established from", client.transport.getHost().host, client.transport.getHost().port
    
  def clientDisconnected(self, client, reason):
    if reason.check(error.ConnectionDone):
      print "Client connection closed normally."
    else:
      print "Client connection error..."
      reason.printTraceback()
  
  def connectedToFaultManager(self, connector):
    print "Connection to fault manager established."
    self._faultManagerConnector = connector
    reactor.callLater(2, self._sendLoadToFaultManager)
    
  def disconnectedFromFaultManager(self, connector, reason):
    print "Fault manager disconnected (did it crash?)"
    if reason.check(error.ConnectionDone):
      print "Fault manager connection closed normally."
    else:
      print "Fault manager connection error..."
      reason.printTraceback()
    
  def connectedToBackup(self, connector):
    stateMessage = "s," + str(self._state)
    print "Connected to backup, sending it current state:", stateMessage
    connector.sendLine(stateMessage)
    connector.transport.loseConnection()
    
  def processMessage(self, client, msg):
    print "Server got message", msg
    operation = msg[0:1] #message type is the first character of the message
    if operation == "a":
      self._performComputation(client, msg[2:])
    elif operation == "u":
      self._updateReplicaList(msg[2:]) #The replicaUpdate message accepts the rest of the payload as a string
    elif operation == "s":
      self._updateState(msg[2:])
    else:
      print "Unknown operation"
      
  def _performComputation(self, client, valueMessage):
    value = int(valueMessage)
    (returnValue, self._state) = self._serverImplementation.compute(value, self._state)
    #send value back to client
    client.sendLine("b," + str(returnValue))
    #send state to other replicas
    self._backupState()
    
  def _updateState(self, stateMessage):
    print "Updating state; new state is:", stateMessage
    self._state = int(stateMessage)
      
  def _updateReplicaList(self, newListMessage):
    if(newListMessage != ""):
      #make a list out of the string we received
      unprocessedReplicaList = newListMessage.split(",")
      #now break these up into (ip, port) pairs (where IP is a string, and port is an integer)
      self._replicaList = [ (address.split(":")[0], int(address.split(":")[1])) for address in unprocessedReplicaList]
      print "Got replicas:", self._replicaList
      
  def _backupState(self):
    for (address, port) in self._replicaList:
      if not (address == self._localAddress and port == self._localPort): #don't connect to ourselves
        factory = Factory()
        factory.protocol = ServerProtocol
        factory.messageProcessor = self
        factory.onConnect = self.connectedToBackup
        factory.onDisconnect = None
        point = TCP4ClientEndpoint(reactor, address, port, timeout=2)
        d = point.connect(factory)
    
  def _sendLoadToFaultManager(self):
    (oneMinuteLoad, fiveMinuteLoad, fifteenMinuteLoad) = os.getloadavg() #we only care about the one minute average
    if self._faultManagerConnector != None:
      loadMessage = "r," + str(oneMinuteLoad) + "," + self._localAddress + ":" + str(self._localPort)
      print "Sending load to fault manager:", loadMessage
      self._faultManagerConnector.sendLine(loadMessage)
    #reset update timer (do it in four seconds again)
    reactor.callLater(2, self._sendLoadToFaultManager)
    
class Server:
  def __init__(self, localAddress, localPort, faultManagerAddress, faultManagerPort):
    self._middleware = ServerMiddleware(localAddress, localPort, faultManagerAddress, faultManagerPort, self)
  
  def run(self):
    self._middleware.run()
    
  def getInitialState(self):
    return 0
    
  #contains the server's "business logic"; returns (result, next state)
  def compute(self, value, currentState):
    return ((value + currentState) / 2, 0)
    
if __name__ == "__main__":
  if len(sys.argv) != 5:
    print "Usage:", sys.argv[0], "local-address local-port faultmgr-address faultmgr-port"
    exit(-1)
  
  server = Server(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))
  server.run()
    
    
