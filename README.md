Programming Assignments 1 and 2
==============================

Jonathon Williams, submitted 25 October 2011

Requirements
------------

* Python, on Linux (tested on Ubuntu Linux 11.04)
* Twisted Python (available in Ubuntu's apt package manager as python-twisted;
  this should already be installed in the Assignment 1 ISISCloud image).
  
Running
-------

## Running using the launch script (Homework 2)

 1. Run an instance, which will be the machine you'll run the launch script on.
    Give this machine a public IP address.
 3. Copy the scripts in this directory to the remote instance.  From the current
    directory (the one with this README file in it) on your machine, run:
    
        scp -i <path to your key file> *.py *.sh ubuntu@<instance ip address>:~/
        
    replacing `<path to your key file>` and `<instance ip address>` with the
    appropriate values.
 4. Copy your **key file and novarc** to the home directory of the remote
    instance.  Make sure it's named in the form` <key-name>.pem`, where
    `<key-name>` is the name of your key as used with the `-k` option to
    `euca-run-instances` (i.e. `jwilliams2.pem` if the name of your key were
    `jwilliams2`).
 5. Connect to the remote instance via SSH:
 
        ssh -i <path to your key file> ubuntu@<instance ip address>
 6. Source `novarc`:

        source novarc
 7. Set the name of your key file:
 
        export KEY_NAME=<key-name>
        
    where `<key-name>` is the name of your key, without the `.pem` suffix (i.e.
    `export KEY_NAME=jwilliams`).
 8. Run the script, and follow any on-screen instructions:
 
        ./launch_test.sh
        
### Notes

  * ISISCloud is still a bit unreliable...  if an instance fails to run or SSH
    into the instance doesn't work, the script will fail.  You should be able to
    press Ctrl+C to stop the script, then kill the instances it created and
    restart the script to try again.
  * Log files are left in the same directory as the launch script:  these
    contain the standard output of the test scripts to verify that they're
    working correctly.
 
## Running manually

Each program needs to be started in a particular order:

1. Fault Manager
2. Server(s)
3. Client

Wait a few seconds between starting each component to give things a chance to
start running and stabilize.

#### Running the fault manager

From a command line:

    python FaultManager.py <port>
    
replacing `<port>` with a port number of your choice (needs to not be in use, and
should be greater than 1024 to run as a regular user).  Remember this number; it
is needed by the client and servers.

#### Running the servers

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

##### UseCpu.py:  program to use an arbitrary amount of CPU time

A program to consume an arbitrary amount of CPU time is also provided.  This can
be run from the command line:

    python UseCpu.py <percentage>
    
where `percentage` is a rough amount of CPU to consume.

#### Running the client

The client runs in a loop, sending a request to the active server replica
approximately every ten seconds, then printing the results (or an error message
if no replicas are available).

From a command line:

    python Client.py <fault-manager-ip> <fault-manager-port>
    
Required parameters:

* `fault-manager-ip`:  The IP address of the fault manager.
* `fault-manager-port`:  The port number of the fault manager.