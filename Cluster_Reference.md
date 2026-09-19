# Cluster reference

[Home](Home.md)

## Services

Complete the [network and certificate setup](Getting_started.md) before opening these internal services.

| Service | Purpose |
| --- | --- |
| [Cluster portal](https://cvgl.lab/) | Service discovery |
| [Determined](https://gpu.cvgl.lab/) | Task scheduling, logs and lifecycle |
| [Harbor](https://harbor.cvgl.lab/) | Container images |
| [Grafana](https://grafana.cvgl.lab/) | Utilization, monitoring and alerts |
| [Nextcloud](https://pan.cvgl.lab/) | File sharing |
| [Weights & Biases](https://wandb.cvgl.lab/) | Experiment tracking |
| [FRP](https://frp.cvgl.lab/) | Administrator-managed forwarding |

Use your own account and request only the services needed for your work. Obtain share links and credentials from the administrator, not from public examples.

## How the components fit together

Your computer connects to the login node for file access, and to Determined for scheduling. Determined starts containers on compute nodes. A container sees shared storage only through its configured bind mounts. Harbor supplies the image; Grafana monitors resource use. The watchdog uses Grafana alerts to reclaim idle shells.

The login node, your computer and a task container have separate filesystems and authentication contexts. A successful SSH connection does not grant Determined or Harbor access. The same path string on two machines does not establish that they share a filesystem.

## Resource and storage inventory

Use the live Determined resource-pool and agent inventory for scheduling decisions. Pool names, healthy agents, allocated slots and auxiliary-container capacity can change independently. [Task submission](Determined_AI_User_Guide.md) explains the checks.

See [shared storage](Shared_Storage.md) for the configured storage families, and [hardware inventory](Hardware_Inventory.md) for the original equipment record. Neither page guarantees current mount health, free capacity or backup coverage.

## Configuration sources

The deployed Determined master reported version **0.38.1** when checked on **2026-09-20**. Use the matching CLI version in the task guide, and recheck compatibility when the master is upgraded.

- [cluster-setup](https://github.com/WU-CVGL/cluster-setup) contains infrastructure definitions, including mounts, Determined configuration and watchdog code. The deployed checkout may contain changes that have not reached the repository.
- [determined-compute](https://github.com/WU-CVGL/determined_batch_submit) maintains the compute CLI, MCP service and their configuration reference.
- This guide maintains user workflows. Record the verification date beside deployment-specific policies and recheck them when the corresponding service changes.

The shell policy is documented in [interactive shells](Interactive_Shell.md). The Docker/Harbor compatibility procedure is documented in [container environments](Custom_Containerized_Environment.md).
