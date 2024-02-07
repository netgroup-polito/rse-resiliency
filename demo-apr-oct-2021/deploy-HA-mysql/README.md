# Deploy HA MySQL using Percona XtraDB Operator

The demo has been tested using MYSQL connector v8.2, k3s v1.24.17+k3s1, openPDC v2.4, Percona operator v1.11.0
- Download and install MYSQL connector from [here](https://downloads.mysql.com/archives/c-net)
- Follow this guide in order to install the Operator [click here](https://docs.percona.com/legacy-documentation/percona-operator-for-mysql-pxc/percona-kubernetes-operator-for-pxc-1.11.0.pdf). NOTE: See the next instructions for the necessary adjustments.
- Avoid to create the namespace pxc and the subsequent instruction, otherwise it's necessary to change the namespace from default to pxc in the yaml file of the PDCs.
- Use create secrets instruction only if custom secrets are needed, and in this case it's necessary to modify both value and name of secret (not tested)
- Before applying cr.yaml, it's advisable to add some configuration parameters. Uncomment the lines configuration |, [mysql] and add the following lines: pxc_strict_mode=permissive(to let the manager to modify the DB) and auto_increment_increment=1 (otherwise PDC can't create database)  
- Use the following command to retrieve the root password of the database in case of using the default secret
```
kubectl get secrets cluster1-secrets -o yaml -o jsonpath='{.data.root}' | base64 --decode | tr '\n' ' ' && echo " "
```
- After applying the cr, it's essential to verify the previous configuration(often auto_increment_increment isn't set). Use tthe next command to create a pod with access to MYSQL 
```
kubectl run -i --rm --tty percona-client --image=percona:8.0 --restart=Never -- bash -il 
```
then login as root using this command (change root_password with the actual root password)
```
mysql -h cluster1-haproxy -uroot -proot_password
```
- Check parameter using SHOW VARIABLES LIKE 'auto_increment_increment'; Set parameter globally SET GLOBAL auto_increment_increment=1;
- Make the service called "cluster1-haproxy-replicas" as NodePort, then start the PDCs
- To connect to the PDCs, it's necessary to change the port 30006 of the command ssh -L 3306:localhost:30006 -L 8500:localhost:30085 -L 6165:localhost:30065 user@kubernetes-node with the port specified by the cluster1-haproxy-replicas svc when connecting to the lower database, same thing when connecting to the higher DB
- On the openPDC manager, when testing the connection to the DB, navigate to advanced setting and change the version of the MYSQL connector from 6.5.4.0 to 8.2.0.0 

NOTE: openpdc-init container image was obtained using the dockerfile inside the folder container

Old Instructions
- operator can be deleted after having installed and setup the PDCs
- pmuLiveness.yaml contains a Liveness Probe for the PMU.
- PDC configuration (in the yaml file) is slightly different from previous one. 

Nota:
- Folder [containers](./containers) contains an image of openpdc-init slightly different (it satisfies the primary key limit).

# Install Liqo
- Install liqoctl following this guide [here](https://docs.liqo.io/en/v0.10.1/installation/liqoctl.html), in this demo it was installed following the section "Install liqoctl manually"
- Install Liqo in the cluster using this command 
```
liqoctl install k3s --cluster-name demo
```
- Liqo is installed!

# Installing Percona Monitoring and Management (PMM)

- Run this command to install PMM Server:
```
curl -fsSLO https://www.percona.com/get/pmm (or wget https://www.percona.com/get/pmm)
chmod +x pmm
./pmm --interactive
```
- Do Port-Forwarding
- kubectl expose po cluster1-pxc-0/1/2 --type=NodePort --name=mysql-0/1/2
- On PMM WebPage: Configuration -> PMM Inventory -> Add Instance (in order to monitor the three mysql replicas)
