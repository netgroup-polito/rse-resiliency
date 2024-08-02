#!/bin/sh

IS_MASTER=0
IS_WORKER=0
MASTER_IP=0
TOKEN=politorse
POD_CIDR=""
SVC_CIDR=""

while getopts :mwht:i:p:s: opt; do
  case $opt in
    m) IS_MASTER=1
       ;;
    i) MASTER_IP=$OPTARG
       ;;
    w) IS_WORKER=1
       ;;
    t) if [ -n "$OPTARG" ]; then TOKEN=$OPTARG; fi
       ;;
    p) POD_CIDR=$OPTARG
       ;;
    s) SVC_CIDR=$OPTARG
       ;;
    h) echo "Usage:
        Use option -t to specify a token (must be the same during every installation across the same cluster)
        To install the first master of the cluster run this script with option -m -p <pod_cidr> -s <svc_cidr>
        To install and join a master to the cluster run this script with option -m -i <master_ip> -p <pod_cidr> -s <svc_cidr>
        To install and join a worker to the cluster run this script with option -w -i <master_ip>"
       exit 1
       ;;
    \?) echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
  esac
done

echo "Using token \"$TOKEN\""
echo "Pod CIDR: \"$POD_CIDR\""
echo "Service CIDR: \"$SVC_CIDR\""

# Check for mutually exclusive options
if [ $IS_MASTER -eq 1 ] && [ $IS_WORKER -eq 1 ]; then
  echo "Error: Cannot specify both -m (master) and -w (worker) options."
  exit 1
fi

# Validate presence and non-empty values of -p and -s if either is provided
if [ $IS_MASTER -eq 1 ]; then
  if [ -z "$POD_CIDR" ] || [ -z "$SVC_CIDR" ]; then
    echo "Error: Both -p <pod_cidr> and -s <svc_cidr> must be specified and cannot be empty in master setup."
    exit 1
  fi
fi

#Install first master
if [ $IS_WORKER -eq 0 ] && [ $IS_MASTER -eq 1 ] && [ $MASTER_IP = 0 ]; then
  echo "Setting up first k3s master"
  curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.24.17+k3s1 K3S_TOKEN=$TOKEN sh -s - server --cluster-init $EXTRAS --kube-apiserver-arg="default-not-ready-toleration-seconds=20" --kube-apiserver-arg="default-unreachable-toleration-seconds=20" --write-kubeconfig-mode 644 --cluster-cidr=$POD_CIDR --service-cidr=$SVC_CIDR
  exit 0
fi

#Install worker
if [ $MASTER_IP != 0 ] && [ $IS_WORKER -eq 1 ]; then
  echo "Installing worker"
  curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.24.17+k3s1 K3S_URL=https://$MASTER_IP:6443 K3S_TOKEN=$TOKEN sh -
  exit 0
fi

#Install another master
if [ $IS_MASTER -ne 0 ] && [ $IS_WORKER -eq 0 ] && [ $MASTER_IP != 0 ]; then
  echo "Installing and joining master"
  curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.24.17+k3s1 K3S_TOKEN=$TOKEN sh -s - server --server https://$MASTER_IP:6443 $EXTRAS --kube-apiserver-arg="default-not-ready-toleration-seconds=20" --kube-apiserver-arg="default-unreachable-toleration-seconds=20" --write-kubeconfig-mode 644 --cluster-cidr=$POD_CIDR --service-cidr=$SVC_CIDR
  exit 0
fi

echo "Usage:
Use option -t to specify a token (must be the same during every installation across the same cluster)
To install the first master of the cluster run this script with option -m -p <pod_cidr> -s <svc_cidr>
To install and join a master to the cluster run this script with option -m -i <master_ip> -p <pod_cidr> -s <svc_cidr>
To install and join a worker to the cluster run this script with option -w -i <master_ip>"
