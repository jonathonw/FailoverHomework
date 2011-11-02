#!/usr/bin/env python

from twisted.protocols import basic
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet import error

from datetime import datetime

import sys

class FaultManagerProtocol(basic.LineReceiver):
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
    self._messageProcessor.clientConnected(self)
  
  def connectionLost(self, reason):
    if reason.check(error.ConnectionDone):
      print "Connection closed normally."
    else:
      print "Connection error..."
      reason.printTraceback()
    
class FaultManager:
  def __init__(self, port):
    self._port = port
    self._replicas = {} #set of replicas stored as a dictionary (address: load)
    self._clients = set([]) #set of all clients and replicas (to send replica updates to)
  
  def runServer(self):
    self._listen()
    #set up periodical replica updates (every four seconds)
    reactor.callLater(4, self._sendReplicaUpdatesToClients)
    reactor.run()
    
  def _listen(self):
    factory = Factory()
    factory.protocol = FaultManagerProtocol
    factory.messageProcessor = self
    point = TCP4ServerEndpoint(reactor, self._port)
    d = point.listen(factory)
    d.addErrback(self._onListenError)
      
  def _onListenError(self, e):
    e.printTraceback()
    reactor.stop()
    return e
    
  def clientConnected(self, client):
    print "Connection established from", client.transport.getHost().host, client.transport.getHost().port
    self._clients.add(client)
    
  def clientDisconnected(self, client):
    self._clients.remove(client)
    
  def processMessage(self, client, msg):
    print "Fault manager got message", msg
    operation = msg[0:1] #message type is the first character of the message
    if operation == "c":
      print "Got a new client"
    elif operation == "r":
      self._replicaUpdate(msg[2:]) #The replicaUpdate message accepts the rest of the payload as a string
    else:
      print "Unknown operation"
      
  def _replicaUpdate(self, replicaMessage):
    
    update = replicaMessage.split(",")
    loadAvg = float(update[0]) #first part of update message is the load average
    address = update[1] #second part is address
    print "Replica at", address, "has load", loadAvg
    self._replicas[address] = loadAvg
    
  def _sendReplicaUpdatesToClients(self):
    sortedReplicas = []
    for key, value in sorted(self._replicas.iteritems(), key=lambda(k,v): (v,k)):
      sortedReplicas.append(key)
    update = "u," + ",".join(sortedReplicas)
    print "Sending replica list to all clients:", update
    for client in self._clients:
      client.sendLine(update)
      
    #reset list of replicas after each periodical update (so that dead replicas
    #will be pruned from the list; since replicas should send an update more
    #frequently than this is called, this shouldn't be a problem for a properly
    #functioning replica
    self._replicas = {}
    
    #reset replica update timer (do it in four seconds again)
    reactor.callLater(4, self._sendReplicaUpdatesToClients)
    
if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "Usage:", sys.argv[0], "port"
    exit(-1)
  
  faultman = FaultManager(int(sys.argv[1]))
  faultman.runServer()
    
    