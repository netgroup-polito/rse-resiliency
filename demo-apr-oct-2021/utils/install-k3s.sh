#!/bin/sh

IS_MASTER=0
IS_WORKER=0
MASTER_IP=0
DEMO_K3S_TOKEN=politorse

# used in case longhorn installation fails
EXTRAS=""

while getopts :mwhtf:s: opt ; do
  case $opt in
    m) IS_MASTER=1
       ;;
    s) MASTER_IP=$OPTARG
       ;;
    w) IS_WORKER=1
       ;;
    t) if test -n $OPTARG; then DEMO_K3S_TOKEN=$OPTARG; fi
       ;;
    # in case longhorn installation fails, setting flannel's backend to wireguard fixes it
    f) EXTRAS="--flannel-backend=\"wireguard\"" 
       ;;
    h) echo "Usage:
Use option -t to specify a token (must be the same during every installation across the same cluster)
To install the first master of the cluster run this script with option -m
To install and join a master to the cluster run this script with option -m -s <master_ip>
To install and join a worker to the cluster run this script with option -w -s <master_ip>

In case longhorn installation get stuck, use option -f to change flannel's backend to wireguard instead of vxlan, to solve overlay issues."; exit 1;;
  esac
done

echo "Using token \"$DEMO_K3S_TOKEN\""

if test $IS_WORKER = 0 -a $IS_MASTER = 1 -a $MASTER_IP = 0; then
  echo "Setting up first k3s master"
  curl -sfL https://get.k3s.io |INSTALL_K3S_VERSION=v1.24.17+k3s1 K3S_TOKEN=$DEMO_K3S_TOKEN sh -s - server --cluster-init $EXTRAS --kube-apiserver-arg="default-not-ready-toleration-seconds=20" --kube-apiserver-arg="default-unreachable-toleration-seconds=20" --write-kubeconfig-mode 644 --cluster-cidr="10.48.0.0/16" --service-cidr="10.50.0.0/16"
  exit 0
fi

if test $MASTER_IP != 0 -a $IS_WORKER = 1; then
  echo "Installing worker"
  curl -sfL https://get.k3s.io |INSTALL_K3S_VERSION=v1.24.17+k3s1 K3S_URL=https://$MASTER_IP:6443 K3S_TOKEN=$DEMO_K3S_TOKEN sh - --cluster-cidr="10.48.0.0/16" --service-cidr="10.50.0.0/16"
  exit 0
fi

if test $IS_MASTER != 0 -a $IS_WORKER = 0 -a $MASTER_IP != 0; then
  echo "Installing and joining master"
  curl -sfL https://get.k3s.io |INSTALL_K3S_VERSION=v1.24.17+k3s1 K3S_TOKEN=$DEMO_K3S_TOKEN sh -s - server --server https://$MASTER_IP:6443 $EXTRAS --kube-apiserver-arg="default-not-ready-toleration-seconds=20" --kube-apiserver-arg="default-unreachable-toleration-seconds=20" --write-kubeconfig-mode 644 --cluster-cidr="10.48.0.0/16" --service-cidr="10.50.0.0/16"
  exit 0
fi

echo "Usage:
Use option -t to specify a token (must be the same during every installation across the same cluster)
To install the first master of the cluster run this script with option -m
To install and join a master to the cluster run this script with option -m -s <master_ip>
To install and join a worker to the cluster run this script with option -w -s <master_ip>

In case longhorn installation get stuck, use option -f to change flannel's backend to wireguard instead of vxlan, to solve overlay issues."
