# Demo - openpdc on kubernetes

The dataset folder contains data and python scripts to generate graphs.

## Containers
The folder [containers](./containers) contains in each subfolder a dockerfile necessary to build the images:
- `pmu` a PMU simulator
- `openpdc` a containerized version of [openpdc](https://github.com/GridProtectionAlliance/openPDC)
- `openpdc-init` an init container to setup the MySQL database and tables
- `adapter` containing PMU and PDC adapters allowing their connection through VerneMQ

Containers can be built for both amd64 and arm64 architectures. However, due to a bug related to mono and qemu, openpdc images must be built on native architectures, otherwise build will fail.
The remaining images can be built using docker's buildx, for example:
```
 docker buildx build \ 
 --push \ 
 --platform linux/arm64/v8,linux/amd64 \ 
 --tag dockerUsername/pmu-cli:latest \
 containers/pmu/
```

## Deployment
The folder [deploy](./deploy) contains the yaml file to deploy the demo in a kubernetes environment. It is possible to customise the deployment editing the yaml files, it is suggested to do so especially in the openPDC deployments:
- if a fake pmu (generated from a local file) is desired, the node id must be set to `e7a5235d-cb6f-4864-a96e-a8686f36e599` and the flag `SAMPLE_DATASET` in the init container must be set to `"true"`. This will generate the necessary configuration in the mysql database.
- the node ID shoul be set as environment variable, otherwise a new one will be generated at each container restart causing issue.

Two possible versions of the demo can be deployed:

- PMU and PDC directly connected through TCP channels
- PMU and PDC connected via [VerneMQ broker](https://vernemq.com/)

The latter case requires the additional deployment of VerneMQ, [PMU and PDC adapters](./containers/adapter), allowing IEEE C37.118 messages to be transported over MQTT messages. OpenPDC should then be connected to PDC adapters instead of connecting it directly to PMUs. For example the hostname for pmu-1 becomes `pdc-pm1-adapter`.
VerneMQ can be easily deployed via [Helm](https://helm.sh/), a default [configuration file](./deploy/vernemq-conf.yaml) is provided, which can be used launching from the repository root directory:

```
helm repo add vernemq https://vernemq.github.io/docker-vernemq
helm repo update
helm install my-vernemq vernemq/vernemq -f deploy/vernemq-conf.yaml
```

### Requirementes:

After having installed k3s using the script in utils (folder documented below):

1. Install Longhorn dependencies:
```
sudo apt install open-iscsi nfs-common
```

2. Install Longhorn (may take some minutes):
If the installations fails, longhorn-csi-plugin and other csi related pods won't start or ui keeps crashing, there might be a network overlay issue. Try enabling the option --flannel-backend="wireguard" in k3s, using the option -f in the provided script in the utils folder.
```
kubectl create namespace longhorn-system
helm repo add longhorn https://charts.longhorn.io
helm repo update
helm install longhorn longhorn/longhorn \
--namespace longhorn-system \
--set defaultSettings.nodeDownPodDeletionPolicy="delete-both-statefulset-and-deployment-pod" \
--set defaultDataLocality="best-effort"
```

## OpenPDC manager
OpenPDC manager is a windows-only application that offers a UI for the database and configuration of an openpdc instance. Since the manager tries to connect to a local service of openPDC, regardless the configuration used, some tweak settings of local port forwarding is necessary in order to connect to a remote instance.

1. Download and install openPDC manager from [here](https://github.com/GridProtectionAlliance/openPDC/releases/tag/v2.4).
1.1 Download and install MySQL Connector from [here](https://dev.mysql.com/downloads/connector/net/6.2.html)

2. If OpenPDC and the manager are already installed on the machine, check that thes service is not running, otherwise the port forwarding in the next step will not work.

32. Enable port forwarding ssh-ing to the remote k8s node using this command (based on the deployment):
Connect to lower-pdc:
```
ssh -L 3306:localhost:30006 -L 8500:localhost:30085 -L 6165:localhost:30065 user@kubernetes-node
```

   Connect to higher-pdc:
```
ssh -L 3306:localhost:30006 -L 8500:localhost:30185 -L 6165:localhost:30165 user@kubernetes-node
```

4. Now run the `ConfigurationSetupUtility.exe` located in the installation folder of openPDC. This will guide you to setup the connection with the database: choose existing configuration and then MySQL.

5. If connecting to the lower level pdc use `openpdc` as user, `lower` as database and `password` as password. If connecting to the higher level pdc use `openpdch` as user, `higher` as database and `password` as password. Test the connection and press next.

6. Generate the configuration only for openPDC Manager and do not start the service openPDC, it is not needed since we are connecting to a remote instance.

7. In openPDC Manager, open the dropdown menu  `System` and click on `Manage Nodes` and in the string inside the `Settings` field change the bit `integratedSecurity=true` to `integratedSecurity=false`. This will enable the remote console and the connection to the remote service.

8. If the instance is **not** the node using the built-in fake pmu/stream then a local historian should be created. In the dropdown menu `Outputs` choose historians and create a new one using a name of your choice and set Type Name to `HistorianAdapters.LocalOutputAdapter`, Assembly Name to `HistorianAdapters.dll`.

9. To add input streams, on the home page, click on Input Device Wizard and follow the guided procedure using the name of the pmu services as host: i.e. for pmu-1 the service is named pmu-1 so host will be set to pmu-1 and port to 4712 (the default port for pmus).

10. To create an output stream, go to the ouputs menu and create a new one. Choose an ID of your choice (should not be already in use) and se the TCP channel to `port=4712;`. Now input streams (PMUs) can be added to this output stream using the configuration wizard link in the table that shows the outputstreams. After that update the configuration of openPDC using the button or from the console with the command `ReloadConfig`.

## Fleet

The demo can be deployed in several clusters, selecting which services should be deployed based on cluster labels. A cluster that acts as "Fleet controller cluster" is necessary so that this will take care of watching the git repo and communicate to downstream clusters which apps should be deployed.
To setup the fleet controller and generate token to join downstream clusters follow the guide [here](https://fleet.rancher.io/multi-cluster-install/).


In our example cluster should be labled either with `site: "primary-station"` or `site: "secondary-station"` and each cluster should have the lavels `zone: italy` `area: A`. To initiate and join a downstream cluster [generate a cluster registration token](https://fleet.rancher.io/cluster-tokens/) and then [install an agent on the selected cluster and join the fleet](https://fleet.rancher.io/agent-initiated/).


Create a cluster group using the resource defined in [groups](./fleet/groups):
```bash
# in the Fleet controller cluster 
kubectl apply -f fleet/groups/cluster-group-italy-area-a.yaml
```

Finally create the `gitrepo` to begin the "watch" of the repo:
```bash
# in the Fleet controller cluster 
kubectl apply -f fleet/gitrepo.yaml
```

### Inter-cluster communication (Liqo)

Once we go for a multi-cluster deployment, there could be the need to make the multiple clusters exchange data. Exposing the services could be a possible solution, making them reachable from the outside, so that even the other clusters are able to reach the service. We decided to have a single VerneMQ deployment for each cluster, seperatly exposing each of them, since each publisher and subscriber accessing the MQTT broker should be redirected to the closest instance, in order to avoid inefficient paths of the traffic. Even though each K3s cluster has its own VerneMQ deployment, the instances can join the same _VerneMQ cluster_ so that all the messages published in an instance of the cluster can be received by performing a subscription to any other instance of the same cluster. For example, all the data published in a VerneMQ instances of the primary station can be received perfoming a subscription to VerneMQ instance placed in the secondary station. This solution allows to obtain a _data-centric architecture_, where anyone can consume the data produced in the area without even knowing who is producing it and where it is located. Unfortunately, all the instances belonging to the same cluster need to directly talk, this means that instances from different clusters need to directly communicate in order to synchronize and exchange messages. [Liqo](https://liqo.io/) is a tool for sharing resources between different Kubernetes clusters, it allows network flattening, automatically setting up all the needed rules and the VPN tunnels, making reachable pods and services from different clusters.
In order to enable communication between clusters we firstly need to install `liqoctl` in the machine where the remote clusters are controlled. Once this is done it is possible to call, for each cluster but the main one, the following command:

```
liqoctl install k3s
```

This command installs all the CRDs, Operators and perform all the needed operations to make Liqo work. Moreover, it generates, as output, a command allowing to perform the peering with the current cluster. Once all the clusters have Liqo running, it is possible to launch from the main cluster each of the join commands generated by the clusters we need to connect. Once Liqo has been correctly deployed, it is possible to create a namespace with the resource offloading, so that clusters can share the resources in that namespace. 

```sh
# Create the namespace
kubectl create namespace communication

# Enable the offloading of the resource inside the namespace
kubectl apply -f deploy/Liqo/ns-offloading.yaml
```

At this point, we can proceed with the VerneMQ cluster deployment with Helm in the shared namespace.

***
**⚠️ IMPORTANT:** At the moment of writing this solution does not work, due to a bug with the virtual kubelet used by Liqo. The downward APIs do not respond with the right pod name. This causes some problems with DNS name resolution, preventing VerneMQ from performing the Kubernetes autoclustering, the feature allowing VerneMQ instances to automatically discover all the others, in order to join the VerneMQ cluster. This bug should be fixed in the next releases, but a [temporary workaround](./deploy/Liqo/bug-workaround) is provided in the [deploy](./deploy) folder.
***

## Utils

The folder [utils](./utils) contains some helper scripts:
- [install-k3s.sh](./utils/install-k3s.sh) installs k3s as master or workers, run this script with the option -h to see some examples on how to use it. In case of troubles installing longhorn use the option -f as documented.
- [install-etcd.sh](./utils/install-etcd.sh) installs etcd and etcdctl, necessary to run the get-leader script.
- [get-leader.sh](./utils/get-leader.sh) prints out the table of the etcd cluster and shows which one is the leader, showing node names instead of ip addresses for easier understanding.
- [isolate-current-node.sh](./utils/isolate-current-node.sh) based on the node in which is executed, sets up the necessary iptables rules to block the traffic to and from other nodes of the cluster. It also takes care of deleting the rules.

***
The demo has been tested with k3s version v1.21.5+k3s2 and longhorn version 1.2.2