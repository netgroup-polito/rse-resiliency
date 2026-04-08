# How to simulate the exchanged traffic when a Pod failure occurs?

## Creating Private Key and Public Key
`ssh-keygen -t rsa`
***
## Install Paramiko
```
sudo apt-get install python3-pip
pip install paramiko
```
***
## Install Remotecap
**A small utility to perform tcpdump packet captures remotely and stream the results back via SSH. It displays the capture file sizes and growth rates**

`pip install remotecap[dev]`

Source: [remotecap](https://github.com/evanfoster/remotecap)

**⚠️ ALERT:** if the installation fails it is likely that **libkrb5-dev** is missing. Install it using:
`sudo apt-get install libkrb5-dev`

***
## Install Tshark
**It lets you read packets from a previously saved capture file**
`sudo apt-get install tshark`
***
## Execution
You need 3 shells:
1.	Execution of [tcpdump](./tcpdump.sh) script, as explained below
2.	Simulation failure pod (run [loopDeletePod](./loopDeletePod.sh) script or command *kubectl delete po <pmu-1-xxxxxx>*)
3.	Retrieve current status of Pod, according to Kubernetes (run status-pod.sh script) 

**With filter**
`./tcpdump.sh <name-pod> “<filter>”`

**Without filter**
`./tcpdump.sh <name-pod>`

*Password:* net

**⚠️ NB:** also, a substring of the pod name is fine. I mean, you don’t have to write "openpdc-lower-22rcdfaf", but just "openpdc-lower" is fine.

If the command returns this error:
*TypeError: private_key() missing 1 required positional argument: 'backend'*
Install: 
`python3 -m pip install --upgrade pyjwt[crypto]`

***
If you want to know the traffic exchanged by the **low level PDC** run:
`./tcpdump.sh openpdc-lower “<filter>”`
In this way you can analyze the traffic that the PMUs send to the low-level PDC and the traffic exchanged by the two PDCs.
For example, you can:
- Simulate failure of a PMU and see the exchanged traffic (*Suggestion*: apply a filter so as to know only the traffic of a specific PMU; e.g. inserting IP of the service on which the PMU is exposed)

If you want to know the traffic exchanged by the **high level PDC** run:
`./tcpdump.sh openpdc-higher`
In this way you can analyze the traffic that the low-level PDC sends to the high-level PDC.
For example, you can:
- Simulate failure of the low-level PDC
***