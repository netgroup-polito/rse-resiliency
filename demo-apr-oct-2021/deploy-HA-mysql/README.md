# Deploy HA MySQL using Percona XtraDB Operator

- Follow this guide in order to install the Operator [click here](https://www.percona.com/doc/kubernetes-operator-for-pxc/kubernetes.html)
- Before doing the PDC apply run these 2 commands: (1) SET GLOBAL auto_increment_increment=1; and (2) Make the service called "cluster1-haproxy" as NodePort
- Once the PDCs are configured, you can delete Operator's deployment.

- pmuLiveness.yaml contains a Liveness Probe for the PMU.
- PDCs configuration (in the yaml file) is slightly different from previous one. 

Nota:
- Folder [containers](./containers) contains an image of openpdc-init slightly different (it satisfies the primary key limit).
