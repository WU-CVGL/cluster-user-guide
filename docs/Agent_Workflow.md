# Use the cluster through MCP

[English](Agent_Workflow.md) | [简体中文](Agent_Workflow.zh.md)

[Home](../README.md) · [Task selection](Determined_AI_User_Guide.md)

We recommend connecting your agent to [Determined Cluster MCP](https://github.com/WU-CVGL/determined_cluster_mcp) for routine cluster work. The service exposes storage and compute tools through MCP over stdio. Use a client that can start a stdio MCP server; native CLI workflows remain available for manual operation.

Agents should read [AGENTS.md](../AGENTS.md), then this workflow and the task-specific pages it links. The repository is named `determined_cluster_mcp`; its executables remain `determined-compute` and `determined-compute-mcp`.

For human-led data exploration and visualization, [Jupyter](Jupyter_Notebooks.md) remains an optional native Determined workflow. The current MCP does not accept `kind: notebook`; do not route a Notebook launch through `compute_launch`.

## Give the agent a task

Describe the goal and how to recognize success. Include the shared project path, code revision, input and output paths, preferred image, resource pool and GPU count when known. The agent can reuse an existing verified configuration and ask only for missing requirements. Provide credential-file or SSH-alias references, never secret values.

For example:

> Read the cluster user guide and use the connected Determined Cluster MCP to evaluate the checkpoint in my shared project. Reuse the project's verified image and pool, request one GPU, and avoid queuing. Check the files and capacity, plan a command task with a meaningful name, then launch it and follow its logs. Write results to the shared output directory and report the task ID, exit status and whether the expected metrics file exists. Ask if any required path or setting is missing.

## Connect the service

Use the current repository URL:

```bash
git clone https://github.com/WU-CVGL/determined_cluster_mcp.git
cd determined_cluster_mcp
```

Follow the service's [installation HOWTO](https://github.com/WU-CVGL/determined_cluster_mcp#readme). Configure the executable, absolute profile and database paths, owner namespace and secrets-file path in your MCP client. Keep credentials in the secrets file or supported credential backend; do not include their values in prompts, task names or tool arguments.

The compute profile describes paths on cluster agents and their container mappings. An optional storage-access configuration describes how the MCP server reaches those paths, locally or through the login node. Client storage access does not require a local NFS mount. See the maintained [storage-access reference](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/shared-storage-access.md) for SSH agents, macOS Keychain, password/keyring access and ControlMaster reuse.

The MCP process must inherit a usable `SSH_AUTH_SOCK` when relying on an SSH agent. A ControlMaster socket must be reachable by that process on the same machine. A read-only consultation worker cannot perform credentialed storage transfers or launch tasks. Installing a skill globally is not required to call MCP tools.

## Run a workload

1. Choose a meaningful `name` and `description`, an appropriate task kind and a project directory on [shared storage](Shared_Storage.md). Confirm the image and resource requirements.
2. If files need staging, call `storage_check`, then preview `storage_sync` with `dry_run: true`. Review paths and exclusions before executing with `dry_run: false`. Existing prepared files need no transfer.
3. Call `compute_resources` for the requested pool and slot count. Leave `allow_queue: false` unless queuing is explicitly intended. Zero-slot commands use auxiliary-container capacity and still need a capacity check.
4. Call `compute_plan` and inspect the resolved mounts, working directory, image and task configuration. Planning is offline; it does not verify live capacity, remote file existence or permissions.
5. Call `compute_launch` with a stable `request_id`. Keep both the returned local `task_id` and remote ID. Retry the identical request with the same request ID; investigate uncertain acceptance before creating another task.
6. Follow `compute_status` and `compute_logs`. Verify exit information and the expected shared files or metrics before reporting success. Preview and execute `storage_fetch` when local copies are needed; cancel unused running tasks with `compute_cancel`.

The service checks capacity again before new launches. That check is a snapshot, not a reservation; scheduling races remain possible. Do not silently change the resource pool or enable queuing after a refusal.

## Paths and persistence

Storage tool paths such as `shared_dir`, and task `workdir`/`output_dir`, use the **container namespace** from the compute profile. The service translates storage operations to cluster host paths and then to local or SSH access. A `local_dir` is on the machine running the MCP server, which may differ from the machine displaying the chat.

Keep code, data and outputs on shared storage. Do not pass source directories or archive uploads to Determined. A profile's `read_only: true` forbids writes through the service; it supplements filesystem permissions. Read-only datasets can be read or fetched, while working directories, uploads and output targets must be writable.

The local SQLite database tracks ownership, task identity and retry/reconciliation state. Shared outputs are separate from that database. Clients using the same database and owner can see the same local task records; an owner name is a namespace, not an authentication boundary.

For supported parameters and error handling, use the [service reference](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.md) and the tools exposed by the connected server. Report what was actually verified; a successful submission alone does not prove that the workload succeeded.
