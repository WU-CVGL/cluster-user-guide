# CVGL cluster user guide

Run workloads on the GPU cluster and keep code, datasets, checkpoints and results on shared storage.

1. [Connect to the cluster](Getting_started.md): accounts, network access, certificates and SSH.
2. [Prepare shared storage](Shared_Storage.md): choose your project directory, transfer files and map it into containers.
3. [Run a task](Determined_AI_User_Guide.md): check available capacity, choose an image and launch with a meaningful name.
4. Inspect logs and shared outputs, then release resources when finished.

| Work | Start here |
| --- | --- |
| One-off scripts, evaluation and non-interactive debug runs | [Command tasks](Determined_AI_User_Guide.md) |
| Interactive debugging, VS Code or PyCharm | [Interactive shells](Interactive_Shell.md) |
| Overnight training, recovery or experiment tracking | [Experiment tasks](Determined_AI_User_Guide.md) |
| Let an agent use the cluster | [MCP workflow](Agent_Workflow.md) |
| Build or reuse a container image | [Container environments](Custom_Containerized_Environment.md) |

Check schedulable capacity before submitting; avoid queuing by default. Low GPU utilization does not mean a GPU is unallocated. Shells are subject to the cluster's external idle-reclamation policy; save work to shared storage throughout the session.

Do not upload code or dataset bundles as Determined task context. A container path can be `/SSD/...` or another configured mount; it does not have to be below `/run/determined/workdir/`. Your own computer does not need to mount cluster storage.

[Troubleshooting](Troubleshooting.md) · [Network and remote access](Network_and_Remote_Access.md) · [Cluster reference](Cluster_Reference.md) · [Contributing](CONTRIBUTING.md)
