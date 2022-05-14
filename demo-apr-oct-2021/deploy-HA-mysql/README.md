# Deploy HA MySQL using Percona XtraDB Operator

- Follow this guide in order to install the Operator [click here](https://www.percona.com/doc/kubernetes-operator-for-pxc/kubernetes.html)
- Before doing the PDC apply run these 2 commands: (1) SET GLOBAL auto_increment_increment=1; and (2) Make the service called "cluster1-haproxy-replicas" as NodePort
- Once the PDCs are configured, you can delete Operator's deployment.

- pmuLiveness.yaml contains a Liveness Probe for the PMU.
- PDC configuration (in the yaml file) is slightly different from previous one. 

Nota:
- Folder [containers](./containers) contains an image of openpdc-init slightly different (it satisfies the primary key limit).


# Installing Percona Monitoring and Management (PMM)

- Run this command to install PMM Server:
'''
curl -fsSLO https://www.percona.com/get/pmm (or wget https://www.percona.com/get/pmm)
chmod +x pmm
./pmm --interactive
'''
- Do Port-Forwarding
- kubectl expose po cluster1-pxc-0/1/2 --type=NodePort --name=mysql-0/1/2
- On PMM WebPage: Configuration -> PMM Inventory -> Add Instance (in order to monitor the three mysql replicas)
