# CVGL cluster user guide

[English](README.md) | [简体中文](README.zh.md)

Run workloads on the GPU cluster and keep code, datasets, checkpoints and results on shared storage.

**Recommended: use your agent with [Determined Cluster MCP](https://github.com/WU-CVGL/determined_cluster_mcp).** It provides tools to check storage and schedulable capacity, plan and launch tasks, and track results. Start with the [agent workflow](docs/Agent_Workflow.md); agents reading this repository should start with [AGENTS.md](AGENTS.md).

1. [Connect to the cluster](docs/Getting_started.md): accounts, network access, certificates and SSH.
2. [Prepare shared storage](docs/Shared_Storage.md): choose your project directory, transfer files and map it into containers.
3. [Run a task](docs/Determined_AI_User_Guide.md): check available capacity, choose an image and launch with a meaningful name.
4. Inspect logs and shared outputs, then release resources when finished.

| Work | Start here |
| --- | --- |
| Ask an agent to prepare, run and follow a workload | [MCP workflow — recommended](docs/Agent_Workflow.md) |
| One-off scripts, evaluation and non-interactive debug runs | [Command tasks](docs/Determined_AI_User_Guide.md#run-a-short-command) |
| Interactive debugging, VS Code or PyCharm | [Interactive shells](docs/Interactive_Shell.md) |
| Data exploration, visual analysis and teaching | [Jupyter — optional](docs/Jupyter_Notebooks.md) |
| Overnight training, recovery or experiment tracking | [Experiment tasks](docs/Determined_AI_User_Guide.md#run-a-durable-experiment) |
| Track metrics and compare runs | [Self-hosted W&B](docs/Weights_and_Biases.md) |
| Build or reuse a container image | [Container environments](docs/Custom_Containerized_Environment.md) |

Check schedulable capacity before submitting; avoid queuing by default. Low GPU utilization does not mean a GPU is unallocated. Shells are subject to the cluster's external idle-reclamation policy; save work to shared storage throughout the session.

Do not upload code or dataset bundles as Determined task context. A container path can be `/SSD/...` or another configured mount; it does not have to be below `/run/determined/workdir/`. Your own computer does not need to mount cluster storage.

For manual operation, use the native CLI examples in the task guide. Installation, MCP configuration and tool parameters are maintained in the [MCP repository documentation](https://github.com/WU-CVGL/determined_cluster_mcp#readme).

[Troubleshooting](docs/Troubleshooting.md) · [Network and remote access](docs/Network_and_Remote_Access.md) · [Cluster reference](docs/Cluster_Reference.md) · [Contributing](CONTRIBUTING.md)
