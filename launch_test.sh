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

echo "Script is done...  killing instances"
echo -n "  Fault manager: $fmInstance... "
euca-terminate-instances "$fmInstance"
echo "OK"
