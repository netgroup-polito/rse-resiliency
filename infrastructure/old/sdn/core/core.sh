#!/bin/bash
sudo ifconfig b.1.1 192.168.101.6/24
sudo ovs-vsctl add-port b.1.1 enp0s3
sudo ovs-vsctl add-port b.1.1 enp0s8
sudo ovs-vsctl add-port b.1.1 enp0s9
sudo ovs-vsctl set bridge b.1.1 protocols=OpenFlow13
sudo ovs-vsctl set-controller b.1.1 tcp:192.168.101.5:6653
