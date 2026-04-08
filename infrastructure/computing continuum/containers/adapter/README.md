# PMU and PDC adapters

## Introduction

Current PMUs and PDCs do not allow to use MQTT for message exchange. In order to test synchrophasors delivering via MQTT, there is the need to let them talk with the MQTT broker in a transparent way. This could be reached putting some "adapters" in between PMU, PDC and the MQTT broker.

### PMU adapter

This component stays between PMUs and broker, it acts as PDC, asking the PMU for its data, once the PMU adapter is able to receive the data from the PMU, it can forward it to a topic in the MQTT broker (by default the topic is `pmu_data/pmu-N` where N is the PMU ID). At the moment each PMU adapter can be configured in order to connect to **a single** PMU instance, therefore a PMU adapter per PMU is needed. The [yaml file](../../deploy/pmu-adapter.yaml) with an example of configuration is located in the [deploy](../../deploy) directory of this repository. In the following lines the available flags for the adapter configuration:

```
pmu_adapter.py [-h] [-c 127.0.0.1] [-b 127.0.0.1] [-p 4712] [-P 1883] [-i 1] [-q 1] [-v 1]
```

Optional arguments:

| Flag                   | Description                                                              | Default   |
| ---------------------- | ------------------------------------------------------------------------ |:---------:|
| -c, --client-pmu       | Client PMU address                                                       | 127.0.0.1 |
| -b, --mqtt-broker      | MQTT broker address                                                      | 127.0.0.1 |
| -P, --mqtt-broker-port | MQTT broker port                                                         | 1883      |
| -i, --pdc-id           | Virtual PDC id                                                           | 1         |
| -q, --qos              | MQTT message QoS                                                         | 1         |
| -v, --verbosity        | Verbosity level, possible values are DEBUG=0, INFO=1, WARNING=2, ERROR=3 | 1         |

### PDC adapter

Once synchrophasors are published on the topic of the MQTT broker, a PDC needs to consume this data. It leverages a set of PDC adapters in order to consume the data from PMUs. The PDC adapter, indeed, acts as a PMU, so that the PDC can be configured in order to connect to the adapter, instead of the real PMU, and it will provide all the synchrophasors published by the PMU in the related topic. 

At the moment each PDC requires a PDC adapter for each PMU it needs to connect. The [yaml file](../../deploy/pdc-adapter.yaml) with an example of configuration is located in the [deploy](../../deploy) directory of this repository. In the following lines the available flags for the adapter configuration:

```
pdc_adapter.py [-h] [-b 127.0.0.1] [-P 1883] [-q 1] [-p 4712] [-v 1] PMU_ID PDC_ID
```

Positional arguments:

| Argument | Description                                                                               |
| -------- | ----------------------------------------------------------------------------------------- |
| PMU_ID   | ID of the PMU to be subscribed, the adapter will subscribe to the `pmu_data/PMU_ID` topic |
| PDC_ID   | It represents the id of the PDC to be connected.                                          |

Optional arguments:

| Flag                   | Description                                                              | Default   |
| ---------------------- | ------------------------------------------------------------------------ |:---------:|
| -b, --mqtt-broker      | MQTT broker address                                                      | 127.0.0.1 |
| -P, --mqtt-broker-port | MQTT broker port                                                         | 1883      |
| -p, --adapter-port     | The port exposed by the adapter, where it listens for PDC connections    | 4712      |
| -q, --qos              | MQTT message QoS                                                         | 1         |
| -v, --verbosity        | Verbosity level, possible values are DEBUG=0, INFO=1, WARNING=2, ERROR=3 | 1         |


## Build the containers

PDC and PMU adapter containers can be easily built launching the following commands from this directory:

For the PMU adapter:

```
docker build -f pmu-adapter/Dockerfile -t pmu-mqtt-adapter . 
```

For the PDC adapter:

```
docker build -f pdc-adapter/Dockerfile -t pdc-mqtt-adapter . 
```

## IEEE C37.118.2 communication standard implementation

Both the PDC and the PMU adapters depends on a [python module](https://github.com/iicsys/pypmu/tree/master/synchrophasor) implementing the IEEE C37.118.2 communication standard,  a widely supported standard for the synchrphasors exchange, so that they can retrieve synchrophasors from PMUs and deliver them to the PDC, interacting with existing tools. Further information about the module can be found in [this paper](https://www.researchgate.net/publication/291957604_Python_Implementation_of_IEEE_C37118_Communication_Protocol). 
