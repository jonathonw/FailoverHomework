#!/bin/bash

IMAGE_TYPE="ami-00000026"

datesuffix=`date "+%Y.%m.%d.%H.%M.%S"`

fmout="log-$datesuffix.FaultManager.out"
clientout="log-$datesuffix.Client.out"
server1out="log-$datesuffix.Server1.out"
server2out="log-$datesuffix.Server2.out"
server3out="log-$datesuffix.Server3.out"
server4out="log-$datesuffix.Server4.out"

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

echo "Waiting 20 seconds to make sure servers are up and running..."
sleep 20

echo "Copying scripts to fault manager instance..."
scp -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" *.py ubuntu@$fmIp:~/

echo "Copying scripts to client instance..."
scp -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" *.py ubuntu@$clientIp:~/

echo "Copying scripts to server1 instance..."
scp -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" *.py ubuntu@$server1Ip:~/

echo "Copying scripts to server2 instance..."
scp -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" *.py ubuntu@$server2Ip:~/

echo "Copying scripts to server3 instance..."
scp -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" *.py ubuntu@$server3Ip:~/

echo "Copying scripts to server4 instance..."
scp -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" *.py ubuntu@$server4Ip:~/

echo "Launching fault manager..."
ssh -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" ubuntu@$fmIp python -u FaultManager.py 3000 > $fmout 2>&1 &

echo "Waiting for 10 seconds for the fault manager to stabilize..."
sleep 10

echo "Launching servers..."
echo "  Server 1..."
ssh -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" ubuntu@$server1Ip python -u UseCpu.py 0 &
ssh -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" ubuntu@$server1Ip python -u Server.py $server1Ip 30001 $fmIp 3000 > $server1out 2>&1 &
sleep 3
echo "  Server 2..."
ssh -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" ubuntu@$server2Ip python -u UseCpu.py 30 &
ssh -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" ubuntu@$server2Ip python -u Server.py $server2Ip 30001 $fmIp 3000 > $server2out 2>&1 &
sleep 3
echo "  Server 3..."
ssh -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" ubuntu@$server3Ip python -u UseCpu.py 60 &
ssh -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" ubuntu@$server3Ip python -u Server.py $server3Ip 30001 $fmIp 3000 > $server3out 2>&1 &
sleep 3
echo "  Server 4..."
ssh -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" ubuntu@$server4Ip python -u UseCpu.py 90 &
ssh -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" ubuntu@$server4Ip python -u Server.py $server4Ip 30001 $fmIp 3000 > $server4out 2>&1 &

echo "Waiting for 10 seconds for servers to stabilize..."
sleep 10

echo "Launching client..."
ssh -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" ubuntu@$clientIp python -u Client.py $fmIp 3000 > $clientout 2>&1 &

echo ""
echo "All servers and clients have been launched.  Output from these can"
echo "be found in the current working directory on this machine at:"
echo "  Fault Manager:  $fmout"
echo "  Client:         $clientout"
echo "  Server 1:       $server1out"
echo "  Server 2:       $server2out"
echo "  Server 3:       $server3out"
echo "  Server 4:       $server4out"

echo ""
echo "Letting the servers and client run for two minutes uninterrupted..."
sleep 120

echo ""
read -p "Press enter to kill server 1 (which should be the primary)..."

echo "Killing server 1..."
ssh -i "$KEY_NAME.pem" -o "StrictHostKeyChecking no" ubuntu@$server1Ip killall -INT python &
echo "Server 1 killed.  Server 2 ($server2Ip) should now be the primary."

echo ""
echo "Letting the servers and client run for two minutes uninterrupted..."
sleep 120

echo ""
echo "Test is complete (but servers are still running, if you want to collect"
echo "more output)."
echo ""
read -p "When finished, press enter to terminate instances created by this script..."

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
echo -n "  Server4: $server4Instance... "
euca-terminate-instances "$server4Instance"
echo "OK"
