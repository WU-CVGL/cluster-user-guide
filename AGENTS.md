# Guide for agents

[English](AGENTS.md) | [简体中文](AGENTS.zh.md)

This repository documents CVGL cluster policy and native user workflows. For Determined Cluster MCP operations, follow the canonical [agent instructions](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/AGENTS.md) and [general workflow](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.md). The [compute-service reference](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.md) defines the API and configuration.

Here, an agent is an AI assistant. A **Determined agent** is a compute-node service, and **ssh-agent** holds SSH authentication keys; these are separate components.

## Read only what the task needs

| Task | Read next |
| --- | --- |
| Run or monitor a workload through MCP | [Canonical agent workflow](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.md), then local [task selection](docs/Determined_AI_User_Guide.md) |
| Install or configure MCP | [MCP README](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/README.md) and [compute-service reference](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.md) |
| Access shared storage through MCP | Local [storage layout](docs/Shared_Storage.md) and canonical [storage-access reference](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/shared-storage-access.md) |
| Troubleshoot MCP | [Canonical MCP troubleshooting](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/troubleshooting.md), then local [cluster troubleshooting](docs/Troubleshooting.md) for network, certificates, mounts, Buildx, and native tasks |
| Configure the optional Codex consultation backend | [Consultation reference](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/consultation.md) |
| Configure cluster login or credentials | [Getting started](docs/Getting_started.md), then [cluster troubleshooting](docs/Troubleshooting.md) |
| Debug interactively or connect an IDE | [Interactive shells](docs/Interactive_Shell.md), including the cleanup policy |
| Explore data or present results in a notebook | [Jupyter](docs/Jupyter_Notebooks.md) for the native Notebook workflow |
| Configure experiment tracking | [Self-hosted W&B](docs/Weights_and_Biases.md); cluster tasks use the 100G LAN endpoint |
| Build an image | [Container environments](docs/Custom_Containerized_Environment.md), with the current [Buildx and Harbor setup](docs/Buildx_and_Harbor.md) |
| Find service URLs or evidence sources | [Cluster reference](docs/Cluster_Reference.md) |
| Edit this documentation | [Contributing](CONTRIBUTING.md) |

Every documentation page has a `.zh.md` counterpart. Use the reader's preferred language. Commands, configuration keys and paths have the same meaning in both versions.

## Site-specific points

- The cluster currently runs Determined `0.38.1`; native clients should use the matching version.
- Use `command` for short non-interactive work, `shell` for interactive debugging, native `notebook` for optional human-led exploration, and `experiment` for long training or experiment lifecycle features.
- Keep code, data and outputs on mapped shared storage. Do not upload project contexts or code/data bundles through Determined. A user's computer does not need to mount cluster storage.
- Check live scheduler state before native submissions. Low GPU utilization does not prove that slots are free, and native `det` submissions can queue.
- The shell watchdog uses sustained GPU utilization rather than keyboard inactivity. Native Notebook tasks are managed separately by the administrator.
- Use the cluster's 100G LAN W&B endpoint from compute tasks. Follow the local network, certificate, storage, Harbor, and shell-policy pages for deployment-specific behavior.

## Documentation maintenance

Use live observations for current capacity and status, repository configuration for policy, and older environment recipes only as starting points. Do not turn the shell's GPU-based cleanup policy into a keyboard-inactivity timeout.

Update English and Chinese together, preserve language links and stable section anchors, and run `python scripts/check_docs.py`. Keep MCP setup, operational rules, API details, and troubleshooting in `WU-CVGL/determined_cluster_mcp`; link its canonical documents instead of copying them here.
