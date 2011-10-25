Programming Assignment 1
========================

Jonathon Williams, submitted 25 October 2011

Requirements
------------

* Python, on Linux (tested on Ubuntu Linux 11.04)
* Twisted Python (available in Ubuntu's apt package manager as python-twisted;
  this should already be installed in the Assignment 1 ISISCloud image).
  
Running
-------

Each program needs to be started in a particular order:

1. Fault Manager
2. Server(s)
3. Client

Wait a few seconds between starting each component to give things a chance to
start running and stabilize.

### Running the fault manager

From a command line:

    python FaultManager.py <port>
    
replacing <port> with a port number of your choice (needs to not be in use, and
should be greater than 1024 to run as a regular user).  Remember this number; it
is needed by the client and servers.

### Running the servers

From a command line:

    python Server.py <local-ip> <local-port> <fault-manager-ip> <fault-manager-port>
    
Required parameters:

* `local-ip`:  The IP address of the machine this server is running on.  This
  should be the IP where the fault manager can reach this replica.
* `local-port`:  An arbitrary port number of your choice (greater than 1024). If
  more than one server or the fault manager is running on the same machine,
  these values must all be different.
* `fault-manager-ip`:  The IP address of the fault manager.
* `fault-manager-port`:  The port number of the fault manager.

#### UseCpu.py:  program to use an arbitrary amount of CPU time

A program to consume an arbitrary amount of CPU time is also provided.  This can
be run from the command line:

    python UseCpu.py <percentage>
    
where `percentage` is a rough amount of CPU to consume.

### Running the client

The client runs in a loop, sending a request to the active server replica
approximately every ten seconds, then printing the results (or an error message
if no replicas are available).

From a command line:

    python Client.py <fault-manager-ip> <fault-manager-port>
    
Required parameters:

* `fault-manager-ip`:  The IP address of the fault manager.
* `fault-manager-port`:  The port number of the fault manager.