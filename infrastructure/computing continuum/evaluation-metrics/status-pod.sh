#!/bin/bash

## Simple script to check the status of a pod.

# pod is the pod name
pod=$1
[ -z "${pod}" ] && echo "ERROR: Pod name not passed" && exit 1

# ns is namespace. Defaults to 'default'
ns=$2
[ -z "${ns}" ] && ns='default'

# Get the pod record from 'kubectl get pods'
while true
do
        p=$(kubectl get pods --namespace ${ns} | grep  "${pod}")
        
        echo "$p" | while read -r line
        do
        
		if  [[ "${line}"  =~ .*"${pod}".* ]]; then
            pod_name=$(echo -n "${line}" | awk '{print $1}')
            ready=$(echo -n "${line}" | awk '{print $2}')
            ready_actual=$(echo -n "${ready}" | awk -F/ '{print $1}')
            status=$(echo -n "${line}" | awk '{print $3}')

            echo "pod ${pod_name}; ready is ${ready}; ready_actual is ${ready_actual};  status is ${status}; at time $(date +%s)"
        else
            echo "ERROR: Pod ${pod} not found"
        fi
        
		done
done

exit

