from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint

class Greeter(Protocol):
  def sendMessage(self, msg):
    self.transport.write("MESSAGE %s\n" % msg)

def gotProtocol(p):
  p.sendMessage("Hello")
  reactor.callLater(1, p.sendMessage, "This is sent in a second")
  reactor.callLater(2, p.transport.loseConnection)
    
def gotError(e):
  print "Error occurred"
  e.printTraceback()
  reactor.stop()
  return e

factory = Factory()
factory.protocol = Greeter
point = TCP4ClientEndpoint(reactor, "129.59.140.57", 1234)
d = point.connect(factory)
d.addCallback(gotProtocol)
d.addErrback(gotError)
reactor.run()
