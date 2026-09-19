# Use the cluster through MCP

[Home](Home.md) · [Task selection](Determined_AI_User_Guide.md)

The [determined-compute service](https://github.com/WU-CVGL/determined_batch_submit) exposes storage and compute tools through MCP over stdio. Use it with a client that supports stdio MCP servers. Native CLI workflows remain available without an agent.

## Connect the service

Follow the service's [installation HOWTO](https://github.com/WU-CVGL/determined_batch_submit#readme). Configure the executable, absolute profile and database paths, owner namespace and secrets-file path in your MCP client. Keep credentials in the secrets file or supported credential backend; do not include their values in prompts, task names or tool arguments.

The compute profile describes paths on cluster agents and their container mappings. An optional storage-access configuration describes how the MCP server reaches those paths, locally or through the login node. Client storage access does not require a local NFS mount. See the maintained [storage-access reference](https://github.com/WU-CVGL/determined_batch_submit/blob/main/docs/shared-storage-access.md) for SSH agents, macOS Keychain, password/keyring access and ControlMaster reuse.

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

For supported parameters and error handling, use the [service reference](https://github.com/WU-CVGL/determined_batch_submit/blob/main/docs/compute-service.md). This guide does not duplicate the service's API schema.
