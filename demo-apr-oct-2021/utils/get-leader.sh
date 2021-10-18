#!/bin/bash

if test $NODE_1 -o $NODE_2 -o $NODE_3
then
    echo "checking kubectl.."
    if test $(which kubectl)
    then
        echo "kubectl found on this machine"
    else
        echo "kubectl not found on this machine. Install it and configure it or manually set env variables of the master nodes:"
        echo "export NODE_1=<node-1 ip>"
        echo "export NODE_2=<node-2 ip>"
        echo "export NODE_3=<node-3 ip>"
        exit 1;
    fi
   i=0
   for ip in $(kubectl get nodes -o wide --no-headers | awk '{print $6}')
   do
   i=$((i+1))
   export "NODE_${i}=${ip}"
   done
fi

sudo ETCDCTL_ENDPOINTS='https://127.0.0.1:2379' ETCDCTL_CACERT='/var/lib/rancher/k3s/server/tls/etcd/server-ca.crt' ETCDCTL_CERT='/var/lib/rancher/k3s/server/tls/etcd/server-client.crt' ETCDCTL_KEY='/var/lib/rancher/k3s/server/tls/etcd/server-client.key' ETCDCTL_API=3 etcdctl endpoint status --cluster -w table | \
sed 's/'"https:\/\/${NODE_1}:2379"'/          node-1          /;s/'"https:\/\/${NODE_2}:2379"'/          node-2          /;s/'"https:\/\/${NODE_3}:2379"'/          node-3          /'