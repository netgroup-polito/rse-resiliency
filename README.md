## Resilient Synchrophasor Measurement System for Distribution Grids

This repository contains the source code, containerized applications, and configuration manifests for the resilient ICT architecture proposed in our paper, **"Computing continuum: The Pathway Towards a Resilient Synchrophasor Measurement System for Distribution Grids"**.

---

### **Project Overview**
The increasing integration of distributed energy resources requires advanced real-time monitoring of power distribution grids. While **Phasor Measurement Units (PMUs)** provide the necessary high-fidelity data, the underlying Information and Communication Technology (ICT) infrastructure must be resilient against hardware failures, software faults, and network disruptions.

This project introduces a novel **Computing Continuum** paradigm that seamlessly integrates Cloud and Edge resources. By abstracting heterogeneous clusters into a single, borderless pool of resources, the architecture enables:
* **Automated Orchestration:** Simplifies application life-cycle management across distributed infrastructures.
* **Self-Healing Resilience:** Automatically detects failures and migrates **Phasor Data Concentrators (PDCs)** to healthy nodes with minimal downtime.
* **ICT Island Mode:** Maintains local monitoring and data collection even when a substation is disconnected from the central Control Center.


### **Purpose of this Repository**
This repository serves as a complete toolkit for reproducing our experimental results and deploying a resilient synchrophasor measurement chain. It includes:

* **Containerized Components:** Docker-ready versions of **openPDC** for data aggregation and custom PMU simulators.
* **Orchestration Manifests:** Kubernetes and **Liqo** configuration files to establish the computing continuum and define workload affinity/anti-affinity rules.
* **High-Availability Data:** Deployment scripts for **Percona XtraDB** to ensure consistent configuration and measurement persistence across clusters.
* **Reproducibility Guide:** A detailed, step-by-step description to help researchers replicate our failure recovery and latency overhead benchmarks.

