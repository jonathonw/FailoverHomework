#!/bin/bash

IMAGE_TYPE="ami-00000026"

waitForInstance() {
  instanceState="x"
  while [[ "$instanceState" != "running" ]]; do
    instanceState=`euca-describe-instances | grep "$1" | cut -f 6`
    echo "  state: $instanceState"
    sleep 5
  done
}

# Launch Fault Manager VM

fmInstanceRecord=`euca-run-instances -k "$KEY_NAME" $IMAGE_TYPE`

echo "Fault Manager:"
echo "$fmInstanceRecord"

fmInstance=`echo "$fmInstanceRecord" | tail -n 1 | cut -f 2`

echo "Fault Manager instance is instance ID: $fmInstance"

echo "Waiting for fault manager instance to enter running state..."

waitForInstance "$fmInstance"

while [[ "$fmInstanceState" != "running" ]]; do
  fmInstanceState=`euca-describe-instances | grep "$fmInstance" | cut -f 6`
  echo "  state: $fmInstanceState"
  sleep 5
done

echo "Fault manager instance is now running...  getting IP"
fmIp=`euca-describe-instances | grep "$fmInstance" | cut -f 4`
echo "Fault manager IP is: $fmIp"

# Launch Client VM

clientInstanceRecord=`euca-run-instances -k "$KEY_NAME" $IMAGE_TYPE`

echo "Client:"
echo "$clientInstanceRecord"

clientInstance=`echo "$clientInstanceRecord" | tail -n 1 | cut -f 2`

echo "Client instance is instance ID: $clientInstance"

echo "Waiting for client instance to enter running state..."

waitForInstance "$clientInstance"

while [[ "$clientInstanceState" != "running" ]]; do
  clientInstanceState=`euca-describe-instances | grep "$clientInstance" | cut -f 6`
  echo "  state: $clientInstanceState"
  sleep 5
done

echo "Client instance is now running...  getting IP"
clientIp=`euca-describe-instances | grep "$clientInstance" | cut -f 4`
echo "Client IP is: $clientIp"

# Launch Server1 VM

server1InstanceRecord=`euca-run-instances -k "$KEY_NAME" $IMAGE_TYPE`

echo "Server1:"
echo "$server1InstanceRecord"

server1Instance=`echo "$server1InstanceRecord" | tail -n 1 | cut -f 2`

echo "Server1 instance is instance ID: $server1Instance"

echo "Waiting for server1 instance to enter running state..."

waitForInstance "$server1Instance"

while [[ "$server1InstanceState" != "running" ]]; do
  server1InstanceState=`euca-describe-instances | grep "$server1Instance" | cut -f 6`
  echo "  state: $server1InstanceState"
  sleep 5
done

echo "Server1 instance is now running...  getting IP"
server1Ip=`euca-describe-instances | grep "$server1Instance" | cut -f 4`
echo "Server1 IP is: $server1Ip"

# Launch Server2 VM

server2InstanceRecord=`euca-run-instances -k "$KEY_NAME" $IMAGE_TYPE`

echo "Server2:"
echo "$server2InstanceRecord"

server2Instance=`echo "$server2InstanceRecord" | tail -n 1 | cut -f 2`

echo "Server2 instance is instance ID: $server2Instance"

echo "Waiting for server2 instance to enter running state..."

waitForInstance "$server2Instance"

while [[ "$server2InstanceState" != "running" ]]; do
  server2InstanceState=`euca-describe-instances | grep "$server2Instance" | cut -f 6`
  echo "  state: $server2InstanceState"
  sleep 5
done

echo "Server2 instance is now running...  getting IP"
server2Ip=`euca-describe-instances | grep "$server2Instance" | cut -f 4`
echo "Server2 IP is: $server2Ip"

# Launch Server3 VM

server3InstanceRecord=`euca-run-instances -k "$KEY_NAME" $IMAGE_TYPE`

echo "Server3:"
echo "$server3InstanceRecord"

server3Instance=`echo "$server3InstanceRecord" | tail -n 1 | cut -f 2`

echo "Server3 instance is instance ID: $server3Instance"

echo "Waiting for server3 instance to enter running state..."

waitForInstance "$server3Instance"

while [[ "$server3InstanceState" != "running" ]]; do
  server3InstanceState=`euca-describe-instances | grep "$server3Instance" | cut -f 6`
  echo "  state: $server3InstanceState"
  sleep 5
done

echo "Server3 instance is now running...  getting IP"
server3Ip=`euca-describe-instances | grep "$server3Instance" | cut -f 4`
echo "Server3 IP is: $server3Ip"

# Launch Server4 VM

server4InstanceRecord=`euca-run-instances -k "$KEY_NAME" $IMAGE_TYPE`

echo "Server4:"
echo "$server4InstanceRecord"

server4Instance=`echo "$server4InstanceRecord" | tail -n 1 | cut -f 2`

echo "Server4 instance is instance ID: $server4Instance"

echo "Waiting for server4 instance to enter running state..."

waitForInstance "$server4Instance"

while [[ "$server4InstanceState" != "running" ]]; do
  server4InstanceState=`euca-describe-instances | grep "$server4Instance" | cut -f 6`
  echo "  state: $server4InstanceState"
  sleep 5
done

echo "Server4 instance is now running...  getting IP"
server4Ip=`euca-describe-instances | grep "$server4Instance" | cut -f 4`
echo "Server4 IP is: $server4Ip"

read -p "Press enter to terminate instances..."

echo "Script is done...  killing instances"
echo -n "  Fault manager: $fmInstance... "
euca-terminate-instances "$fmInstance"
echo "OK"
echo -n "  Client: $clientInstance... "
euca-terminate-instances "$clientInstance"
echo "OK"
echo -n "  Server1: $server1Instance... "
euca-terminate-instances "$server1Instance"
echo "OK"
echo -n "  Server2: $server2Instance... "
euca-terminate-instances "$server2Instance"
echo "OK"
echo -n "  Server3: $server3Instance... "
euca-terminate-instances "$server3Instance"
echo "OK"
echo -n "  Server4: $server3Instance... "
euca-terminate-instances "$server3Instance"
echo "OK"
