# Guide for agents

[English](AGENTS.md) | [简体中文](AGENTS.zh.md)

This repository documents CVGL cluster use. For operational work, prefer the connected [Determined Cluster MCP](https://github.com/WU-CVGL/determined_cluster_mcp); its tool schemas and service documentation define the API. This repository supplies cluster policy and user workflows.

Here, an agent is an AI assistant. A **Determined agent** is a compute-node service, and **ssh-agent** holds SSH authentication keys; these are separate components.

## Read only what the task needs

| Task | Read next |
| --- | --- |
| Run or monitor a workload | [Agent workflow](Agent_Workflow.md), then [task selection](Determined_AI_User_Guide.md) |
| Resolve paths or transfer files | [Shared storage](Shared_Storage.md) and the MCP storage-access reference linked there or in the agent workflow |
| Configure login or credentials | [Getting started](Getting_started.md), then [troubleshooting](Troubleshooting.md) |
| Debug interactively or connect an IDE | [Interactive shells](Interactive_Shell.md), including the verified cleanup policy |
| Build an image | [Container environments](Custom_Containerized_Environment.md); retain the Harbor compatibility path |
| Find service URLs or evidence sources | [Cluster reference](Cluster_Reference.md) |
| Edit this documentation | [Contributing](CONTRIBUTING.md) |

Every documentation page has a `.zh.md` counterpart. Use the reader's preferred language. Commands, configuration keys and paths have the same meaning in both versions.

## Operational defaults

- Reuse verified project configuration when available. Resolve required image, pool, slot count, paths and success criteria before launch; ask for missing requirements rather than inventing them.
- Use `command` for short non-interactive work, `shell` for interactive debugging, and `experiment` for overnight training or experiment lifecycle features. Choose a meaningful name and description.
- Keep code, data and outputs on mapped shared storage. Do not upload project contexts or code/data bundles through Determined. Distinguish cluster host, container and MCP-server-local paths; the user's computer need not mount shared storage.
- Check live schedulable capacity and keep `allow_queue: false` unless the user intends to queue. Low GPU utilization is not proof of free slots. A capacity snapshot does not reserve resources.
- Preview storage transfers and inspect their resolved paths before executing within the user's authorized scope. Respect read-only mounts and filesystem permissions. Reading this guide alone does not authorize a launch, transfer or infrastructure change.
- Inspect the plan, then use a stable request ID. After uncertain acceptance, inspect or reconcile the existing record before considering another submission. Follow logs and status, then verify the requested outputs before reporting success.
- Use credential references and existing authenticated sessions. Never place credential values in prompts, task metadata, source, logs or reports.

## Evidence and maintenance

Distinguish live observations, verified configuration and historical examples. Record the date for deployment-specific statements. Do not turn the shell's GPU-based cleanup policy into a keyboard-inactivity timeout, or present historical images as currently tested.

When editing docs, update English and Chinese together, preserve language links and stable section anchors, and run `python scripts/check_docs.py`. Keep example commands and resource requirements consistent across languages. Keep the API reference in the MCP repository rather than duplicating its schema here. No live launch or image build is required merely to translate or check documentation.
