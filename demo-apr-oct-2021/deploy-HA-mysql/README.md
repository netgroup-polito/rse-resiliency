# Deploy HA MySQL using Percona XtraDB Operator

- Follow this guide in order to install the Operator [click here](https://docs.percona.com/legacy-documentation/percona-operator-for-mysql-pxc/percona-kubernetes-operator-for-pxc-1.11.0.pdf). NOTE: avoid to create pxc namespace, otherwise need to change configuration of PDC yaml file
- Use this command kubectl get secrets cluster1-secrets -o yaml -o jsonpath='{.data.root}' | base64 --decode | tr '\n' ' ' && echo " " to discover the root password of the database
-Use these commands to entry the mysql configuration: (1) kubectl run -i --rm --tty percona-client --image=percona:8.0 --restart=Never -- bash -il (2)mysql -h cluster1-haproxy -uroot -proot_password, changing root_password with the 64base string of point 4 
-Set these 2 variables: SET GLOBAL auto_increment_increment=1; SET GLOBAL pxc_strict_mode = PERMISSIVE
-Make the service called "cluster1-haproxy-replicas" as NodePort
- Once the PDCs are configured, you can delete Operator's deployment.

-Change the port 30006 of the command ssh -L 3306:localhost:30006 -L 8500:localhost:30085 -L 6165:localhost:30065 user@kubernetes-node with the port specified by the cluster1-haproxy-replicas svc when connecting to the lower database, same thing for the command ssh -L 3306:localhost:30006 -L 8500:localhost:30185 -L 6165:localhost:30165 user@kubernetes-node
pmuLiveness.yaml contains a Liveness Probe for the PMU.
- PDC configuration (in the yaml file) is slightly different from previous one. 

Nota:
- Folder [containers](./containers) contains an image of openpdc-init slightly different (it satisfies the primary key limit).


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
