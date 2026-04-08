#!/bin/sh

set -e

CURRENT_NODE=$(hostname  -I | cut -f1 -d' ')

if test -z $CURRENT_NODE
then
   echo "Could not determine host IP"
   exit 1
fi

if test $NODE_1 -o $NODE_2 -o $NODE_3 -o $NODE_4
then
    echo "checking kubectl.."
    if test $(which kubectl)
    then
        echo "kubectl found on this machine"
    else
        echo "kubectl not found on this machine. Install it and configure it or manually set env variables of nodes:"
        echo "export NODE_1=<node-1 ip>"
        echo "export NODE_2=<node-2 ip>"
        echo "export NODE_3=<node-3 ip>"
        echo "export NODE_4=<node-4 ip>"
        exit 1;
    fi
   i=0
   for ip in $(kubectl get nodes -o wide --no-headers | awk '{print $6}')
   do
   i=$((i+1))
   export "NODE_${i}=${ip}"
   done
fi


if test ! $NODE_1 -o ! $NODE_2 -o ! $NODE_3 -o ! $NODE_4
then
    echo "kubectl not found on this machine. Install it and configure it or manually set env variables of nodes:"
    echo "export NODE_1=<node-1 ip>"
    echo "export NODE_2=<node-2 ip>"
    echo "export NODE_3=<node-3 ip>"
    echo "export NODE_4=<node-4 ip>"
   exit 1
fi


echo "Host IP: ${CURRENT_NODE}"

if test $CURRENT_NODE != $NODE_1
then
    echo "Blocking traffic to and from node-1: ${NODE_1}"
    sudo iptables -A OUTPUT -j DROP -d ${NODE_1}
    sudo iptables -A INPUT -j DROP -s ${NODE_1}
fi

if test $CURRENT_NODE != $NODE_2
then
    echo "Blocking traffic to and from node-2: ${NODE_2}"
    sudo iptables -A OUTPUT -j DROP -d ${NODE_2}
    sudo iptables -A INPUT -j DROP -s ${NODE_2}
fi

if test $CURRENT_NODE != $NODE_3
then
    echo "Blocking traffic to and from node-3: ${NODE_3}"
    sudo iptables -A INPUT -j DROP -s ${NODE_3}
    sudo iptables -A OUTPUT -j DROP -d ${NODE_3} 
fi

if test $CURRENT_NODE != $NODE_4
then
    echo "Blocking traffic to and from node-4: ${NODE_4}"
    sudo iptables -A OUTPUT -j DROP -d ${NODE_4} 
    sudo iptables -A INPUT -j DROP -s ${NODE_4}
fi

echo "iptables rules updated"
echo "current time for reference:"
date
echo "time in ns for reference:"
date +%s%N

echo ""

echo "Press ENTER to enable again the traffic"
read _

if test $CURRENT_NODE != $NODE_1
then
    echo "Enabling traffic to and from node-1: ${NODE_1}"
    sudo iptables -D OUTPUT -j DROP -d ${NODE_1}
    sudo iptables -D INPUT -j DROP -s ${NODE_1}
fi

if test $CURRENT_NODE != $NODE_2
then
    echo "Enabling traffic to and from node-2: ${NODE_2}"
    sudo iptables -D OUTPUT -j DROP -d ${NODE_2}
    sudo iptables -D INPUT -j DROP -s ${NODE_2}
fi

if test $CURRENT_NODE != $NODE_3
then
    echo "Enabling traffic to and from node-3: ${NODE_3}"
    sudo iptables -D INPUT -j DROP -s ${NODE_3}
    sudo iptables -D OUTPUT -j DROP -d ${NODE_3} 
fi

if test $CURRENT_NODE != $NODE_4
then
    echo "Enabling traffic to and from node-4: ${NODE_4}"
    sudo iptables -D OUTPUT -j DROP -d ${NODE_4} 
    sudo iptables -D INPUT -j DROP -s ${NODE_4}
fi

echo "iptables rules deleted"
echo "current time for reference:"
date