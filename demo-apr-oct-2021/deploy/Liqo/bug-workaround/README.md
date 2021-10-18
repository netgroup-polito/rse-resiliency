# Liqo virtual kubelet bug workaround

This folder contains an example of deployment allowing to use Liqo for direct interaction between the VerneMQ instances, even when they are located in different Kubernetes clusters. This is a workaround for the Liqo bug preventing the usage of the VerneMQ autoclustering, the feature allowing each broker instance to discover all the others in order to perform the join to the VerneMQ cluster. VerneMQ uses StatefulSet in order to launch the broker instances. Whenever Liqo forwards the request of pod creation to the child clusters, it adds a random number to the StatefulSet pod name, in order to avoid conflicts. However, when using the downward APIs in order to obtain the Pod name, the original name is returned, causing some problems with the DNS name resolution. If, instead, we expose each broker instance with a service having the name the downward API provides, the broker instances are able to correctly resolve the name. We provided two examples of deployments for two different clusters connected with Liqo, with the _namespace offloading_ in the `communication` namespace. However, before applying the resources, there is the need to set the node affinity in order to make the StatefulSet run in the desired cluster.

```sh
# From the main cluster
# Get the virtual node name of the corresponding cluster
kubectl get nodes
# Replace the nodeName with the desired one, i.e liqo-ac4816cf-dc76-429e-ab18-646d266700b9
sed -i 's/PutHereYourClusterLiqoName/[NODE_NAME]/g' primary-vernemq-deploy.yaml
sed -i 's/PutHereYourClusterLiqoName/[NODE_NAME]/g' secondary-vernemq-deploy.yaml
# Apply the deployments
kubectl apply -f primary-vernemq-deploy.yaml secondary-vernemq-deploy.yaml
```

Unfortunately, this workaround allows the communication between each single VerneMQ broker instance, but **autoclustering is not possible. Join should be manually done** for each broker instance but one (in this case primary-vernemq-0), by calling in the corresponding pod:

```
kubectl exec [POD_NAME] -- vmq-admin cluster join discovery-node=VerneMQ@primay-vernemq-0.communication.svc.cluster.local 
```
This allows the broker instance to perform the join to the VerneMQ cluster. Once they join, they will know all the other instances belonging to the cluster, and they will start exchanging information.
