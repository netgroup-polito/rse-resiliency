#!/bin/bash

## Script to do tcpdump.

#Dictionary to map name and IP of the nodes.
declare -A nameServerAddress
nameServerAddress[server1]=192.168.0.153
nameServerAddress[server2]=192.168.0.157
nameServerAddress[server3]=192.168.0.160
nameServerAddress[server4]=192.168.0.159

# pod is the pod name
pod=$1
[ -z "${pod}" ] && echo "ERROR: Pod name not passed" && exit 1

filter=$2
#echo $filter

p=$(kubectl get pods -o wide | grep  "${pod}")
pod_name=$(echo -n "${p}" | awk '{print $1}')
server=$(echo -n "${p}" | awk '{print $7}')
numberInterface=$(kubectl exec -it $pod_name  -- cat /sys/class/net/eth0/iflink | tail -1)
ipServer=$(echo ${nameServerAddress[$server]})

nameInterface=`./getNameInterface.py $ipServer $numberInterface`

#Debug
echo $nameInterface

if [ -z "${filter}" ]
   then
        #there is NOT a filter
        ./remotecap.py -w remoteCapture --user net --sudo -i $nameInterface -p $ipServer
else
        #there is a filter
        ./remotecap.py -w remoteCapture --user net --sudo --filter "$filter" -i $nameInterface -p $ipServer
fi

tshark -t a -r remoteCapture