# Install Liqo
- Install liqoctl following this guide [here](https://docs.liqo.io/en/v0.10.1/installation/liqoctl.html). In this demo, it was installed following the section "Install liqoctl manually"
- Liqo supports k3s, but when creating the Liqo cluster, it uses the config in the folder .kube, which our installation script doesn't create (k3s saves the config in another path). After creating the .kube folder (usually in the home directory), use the following command to create the config file:
    ```
    cp /etc/rancher/k3s/k3s.yaml config
    ```
- Install Liqo in the cluster using this command 
    ```
    liqoctl install k3s --cluster-name <cluster-name> --pod-cidr="<cidr-value>" --service-cidr="<cidr-value>"
    ```
    Notes: 
    1) CIDRs specified need to be the same as those of the cluster k3s, otherwise Liqo will give an error
    2) If we use separate pod and service CIDRs by one range, then Liqo will set external CIDR as the range between them. For example, if we use 10.48.0.0/16 for pods and 10.50.0.0/16 for services, Liqo will use 10.49.0.0/16 as the external CIDR.
- To unidirectionally peer two cluster, use this command on the cluster provider (who may give resources)
    ```
    liqoctl generate peer-command
    ```
    and use the output in the cluster customer (who may use these resources)
- To offload a namespace in the cluster provider, forcing the same name, use the following command: 
    ```
    liqoctl offload namespace <namespace-name>   --namespace-mapping-strategy EnforceSameName
    ```
# Deploy HA MySQL using Percona XtraDB Operator

The demo has been tested using MYSQL connector v8.2, k3s v1.24.17+k3s1, openPDC v2.4, Percona operator v1.11.0
- Download and install MYSQL connector from [here](https://downloads.mysql.com/archives/c-net)
- Follow this guide (paragraph advanced installation guide) in order to install the Operator [click here](https://docs.percona.com/legacy-documentation/percona-operator-for-mysql-pxc/percona-kubernetes-operator-for-pxc-1.11.0.pdf). NOTE: See the next instructions for the necessary adjustments.
  - Instead of namespace pxc, use lower or higher based on the need. To avoid confusion, add the specified namespace ("-n lower" or "-n higher") to every instruction after that instead of the subsequent instruction.   
  - Use create secrets instruction only if custom secrets are needed, and in this case it's necessary to modify both value and name of the secret
  - Add the node selector rule in the operator.yaml matching the root cluster, because it needs to see every other cluster
  - Before applying cr.yaml, it's advisable to add some configuration parameters:
  1) Change the name from cluster1 to the appropriate name, but in this case be aware that you need to also change every other command with cluster1 inside 
  2) Uncomment the lines configuration |, [mysql] and add the following lines: pxc_strict_mode=permissive(to let the manager to modify the DB) and auto_increment_increment=1 (otherwise PDC can't create database)
  3) Change the  storageClassName from local-path to liqo
  4) Change the affinity based on the requirements  
  5) In the haproxy sections, uncomment replicasServiceType: and put it as NodePort

- Use the following command to retrieve the root password of the database (if using the default secret)
    ```
    kubectl get secrets cluster1-secrets -n <namespace-name> -o yaml -o jsonpath='{.data.root}' | base64 --decode | tr '\n' ' ' && echo " "
    ```
- After applying the cr, it's essential to verify the previous configuration(auto_increment_increment is bugged, often isn't set). To access to the database manually, we have 2 main options: 
    1) Use the Percona command to create a pod that gives access to a random pxc pod 
        ```
        kubectl run -i -n <namespace-name> --rm --tty percona-client --image=percona:8.0 --restart=Never -- bash -il 
        ```
    2) Enter a specific pxc pod with the following command 
        ```
        kubectl exec -it cluster1-pxc-0 -c pxc -n <namespace> -- bash
        ```
    then login as root using this command (change root_password with the actual root password)
    ```
    mysql -h cluster1-haproxy -uroot -proot_password
    ```
    check parameters with 
    ```
    SHOW VARIABLES LIKE '<name-of-parameter>';
    ``` 
    and set them globally with 
    ```
    SET GLOBAL <name-of-parameter>=<value>;
    ``` 
- To connect with the right port of the DB, it's necessary to change the port 30006 of the command for the PDC-L
    ```
    ssh -L 3306:localhost:30006 -L 8500:localhost:30085 -L 6165:localhost:30065 user@kubernetes-node
    ```   
    with the port specified by the cluster1-haproxy-replicas svc when connecting to the lower database, same thing for the PDC-H
- On the openPDC manager, when testing the connection to the DB, navigate to advanced setting and change the version of the MYSQL connector from 6.5.4.0 to 8.2.0.0 

NOTE: openpdc-init container image was obtained using the dockerfile inside the folder container

Old Instructions
- operator can be deleted after having installed and setup the PDCs
- pmuLiveness.yaml contains a Liveness Probe for the PMU.
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
