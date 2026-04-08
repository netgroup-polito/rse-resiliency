#!/bin/bash

## Simple script to delete a pod every 120 sec.

# pod is the pod name
pod=$1
[ -z "${pod}" ] && echo "ERROR: Pod name not passed" && exit 1


while true
do
    p=$(kubectl get pods | grep  "${pod}")

    if  [[ "${p}"  =~ .*"${pod}".* ]]; then
        pod_name=$(echo -n "${p}" | awk '{print $1}')
        kubectl delete po $pod_name
    else
        echo "ERROR: Pod ${pod} not found"
    fi
        sleep 120
done

exit

