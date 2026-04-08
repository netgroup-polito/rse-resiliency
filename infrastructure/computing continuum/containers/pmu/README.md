# PMU simulator

The provided PMU simulator is a custom version of PMUsim, an open-source, C-based, IEEE C37.118-complaint PMU simulator tool, allowing to generate random synchrophasors. It comes with the [iPDC](https://sourceforge.net/projects/iitbpdc/) set of tools and it provides a graphical interface useful for the PMU configuration. Unfortunately, even though the GUI makes configuration easier when users directly interact with the tool, this is not true in a cloud environment. PMUsim allows to store a configuration in a binary file so that it is possible to reload the same configuration once the application is restarted, or to have multiple configurations that can be loaded when needed. The PMUsim source code has been modified in order to launch it, directly loading the configuration file, without the need to start the GUI. This can be done by using the `-i` flag as in the following example:

```sh
PMU -i config_file.bin
```

## Generating a configuration file

The configuration file can created locally via the PMUsim graphical interface. Clicking on `File->New PMU setup` and completing the form with all the parameters, a binary file with the configuration is created in the directory `/home/{USER}/iPDC/PMU/{PMU-NAME}.bin`. This file can be used to create a ConfigMap to be mounted in the Kubernetes PMU pod. For example, in order to create a config map named `pmu-1` with the configuration file `pmu-1.bin`:

```sh
kubectl create configmap pmu-1 --from-file=pmu-1.bin
```

An example of binary configuration files can be found in the directory [/deploy/pmu-config](../../deploy/pmu-config), while [/deploy/pmu.yaml](../../deploy/pmu.yaml) contains the ConfigMaps with the binary configuration of three PMUs (pmu-1, pmu-2 and pmu-3) and the deployment to launch them.
