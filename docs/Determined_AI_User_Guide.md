[English](Determined_AI_User_Guide.md) | [简体中文](Determined_AI_User_Guide.zh.md)

# Determined AI: practical user guide

For agent-assisted work, use the canonical [Determined Cluster MCP workflow](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.md). This page explains cluster task selection and provides native CLI commands for manual operation.

Determined runs containerized work on the GPU cluster. Keep the durable parts of every job—source code, datasets, checkpoints, and outputs—on shared storage. Treat the task container as temporary.

## Choose the right workload

| Workload | Use it for | Typical lifetime |
| --- | --- | --- |
| **Command** | Short, non-interactive evaluation, conversion, or preprocessing | Minutes to hours |
| **Shell** | Interactive debugging, IDE access, and environment inspection | While actively debugging |
| **Notebook** (optional, native CLI) | Data exploration, visual analysis and teaching | While actively analyzing |
| **Experiment** | Long or overnight training, checkpointing, restart, and trial tracking | Hours to days |

Use a command by default for one-off work, including short unattended jobs. Use a shell when a person needs to interact with the process. Use an experiment for overnight training or when checkpoint recovery and trial tracking are needed.

[Jupyter](Jupyter_Notebooks.md) is an optional native interface for interactive research. Long-idle native Notebook tasks are currently stopped manually by the administrator; the shell watchdog does not manage them. See the canonical [compute-service reference](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.md) for MCP-supported task kinds.

Give every task a short, meaningful name and a description that says what it runs. Names such as `evaluate-checkpoint-240k` are easier to operate than UUIDs or `test`.

Native command and shell configs expose one `description` field, so put the short display name on its first line and the purpose on following lines. Experiments have separate `name` and `description` fields.

## Install and authenticate

The cluster runs [WU-CVGL/determined](https://github.com/WU-CVGL/determined), a fork of Determined. Install the fork's CLI from its release, in the cluster's version. First set the version and the release wheel:

```bash
DET_VERSION=0.42.0
DET_WHEEL="https://github.com/WU-CVGL/determined/releases/download/$DET_VERSION/determined-$DET_VERSION-py3-none-any.whl"
```

On the login node, install it for your account:

```bash
python3 -m pip install --user "$DET_WHEEL"
det --version
```

pip may warn that `~/.local/bin` is not on `PATH`. You can ignore the warning.

On your own device, use Python 3.8 or later, in a virtual environment:

```bash
python3 -m venv ~/.venvs/det
source ~/.venvs/det/bin/activate
python -m pip install "$DET_WHEEL"
det --version
```

Run the `source` line again in each new shell. On Windows, the activate script is `~/.venvs/det/Scripts/activate`.

Do not run `pip install determined`: it installs the upstream CLI. If downloads from GitHub or PyPI are slow or fail, use a [proxy or mirror](Network_and_Remote_Access.md#proxies-and-mirrors).

The login node already has the cluster CA; on your own device, follow the [certificate setup](Getting_started.md#3-enroll-the-cluster-ca-when-required). Set `DET_MASTER_CERT_FILE` to the downloaded `cvgl.crt` only if the CLI still needs an explicit CA path:

```bash
export DET_MASTER=https://gpu.cvgl.lab
# If needed: export DET_MASTER_CERT_FILE=/absolute/path/to/cvgl.crt
det user login <username>
```

The CLI must match the cluster's version. `det version` shows the CLI and master versions, and `det` warns when they differ. Then repeat the install with `DET_VERSION` set to the master's version. An older CLI can fail, for example when you change your password. See [Cluster Reference](Cluster_Reference.md) for the live service and configuration sources.

Check authentication before launching work:

```bash
det user whoami
```

## Put all durable files on shared storage

A typical mapping is:

| Host path | Container path | Purpose |
| --- | --- | --- |
| `/workspace/<username>` | `/run/determined/workdir/home` | Code, checkpoints, and outputs |
| `/datasets` | `/run/determined/workdir/data` | Shared datasets, normally read-only |

Before launch:

1. Copy or sync the exact code revision to a directory under your shared workspace.
2. Point the task's working directory at that mapped directory.
3. Write results and checkpoints to another mapped directory.
4. Mount datasets from shared storage; do not copy them into a submission context.

The examples in [`examples/compute/`](../examples/compute/) use this layout. Replace every placeholder before use.

Do not pass `--context`, `--include`, or a model-directory argument for this workflow. Native `det experiment create CONFIG` accepts an omitted model-definition argument and therefore sends an empty context.

## Check scheduler capacity

Scheduler slots determine whether a GPU task can start. GPU utilization from `nvidia-smi` does not tell you whether a slot is schedulable.

With the native CLI, inspect current slots and their resource pools:

```bash
det slot list
det slot list --json
```

Count only enabled, non-draining, free slots in the requested pool. Multi-GPU single-node work requires enough free slots on one agent.

Pools are public unless an administrator restricts one. The WebUI does not list a restricted pool that you have no access to, but `det slot list` still shows its slots. A submission to it fails with:

```text
user "<username>" may not use resource pool "<pool>": the pool is restricted; choose another pool or ask an administrator for access (if resources.resource_pool was not set, "<pool>" is the default pool for this workspace or the cluster)
```

Choose another pool with `resources.resource_pool`, or ask the cluster administrator for access.

In the WebUI, open a pool from **Cluster**. Its **Active** tab lists the GPUs each job holds, by node, for example `node07: 0, 2` or `node08: 4-7`. Three or more consecutive GPUs show as a range. The numbers are the node's `nvidia-smi` indexes. Click them to outline the GPUs in the pool's topology panel.

The native `det` launch commands can queue. Capacity can change between inspection and submission, so recheck the submitted task and cancel it if queuing was unintended. MCP capacity and admission behavior is documented in the canonical [compute-service reference](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.md).

## Request well-connected GPUs

For DDP and other jobs that use 2 or more GPUs on one node, set `resources.prefer_gpu_topology`:

```yaml
resources:
  slots_per_trial: 4
  prefer_gpu_topology: soft
```

Commands and shells take the same key next to `resources.slots`.

- `soft` starts the job as soon as it fits, on the best-connected set of free GPUs of its node, ranked by NVLink, peer-to-peer path, NUMA node and PCIe link width. Use it by default.
- `strong` waits until one NUMA node of a node has as many free GPUs as the job asks for, and gives the job those GPUs. Use it when the job is much slower across NUMA nodes and can wait. A waiting job is `QUEUED`, and its log says what it waits for. When no NUMA node in the pool has that many GPUs, the submission is refused, or a queued job fails, with a message that contains `no NUMA node in pool <pool> has <n> slots; use soft`.
- `true` is not a value and is rejected.

Neither value changes a 1-GPU job, and `soft` does not change a job across several nodes. For a job with 2 or more GPUs on one node, the task log has a line starting `GPU topology preference` that names the node and its GPUs.

## Run a short command

Review [`examples/compute/command.yaml`](../examples/compute/command.yaml), then run:

```bash
det command run \
  --config-file examples/compute/command.yaml \
  bash -lc 'mkdir -p /run/determined/workdir/home/results && cd /run/determined/workdir/home/project && python scripts/evaluate.py --output /run/determined/workdir/home/results/eval.json'
```

The command streams logs unless `--detach` is supplied. Reopen logs or stop it with:

```bash
det task logs -f <command-id>
det command kill <command-id>
```

## Start an interactive shell

Review [`examples/compute/shell.yaml`](../examples/compute/shell.yaml), then run:

```bash
det shell start --config-file examples/compute/shell.yaml
```

Use shells for debugging and IDE access. Reconnection, VS Code/PyCharm setup, port forwarding, and the current lifetime guidance are in [Interactive Shell](Interactive_Shell.md).

## Run a durable experiment

Review [`examples/compute/experiment.yaml`](../examples/compute/experiment.yaml). Its entrypoint changes into the shared code directory, and its checkpoint storage is also under the shared workspace.

Submit it without a model-definition directory:

```bash
det experiment create examples/compute/experiment.yaml
```

Do not append `.` or another code directory: that would package and upload files. The experiment reads code and data through bind mounts.

Adapt the example to the training program. Its `searcher.metric: validation_loss` is useful only when the code reports a metric with that exact name to Determined. `checkpoint_storage` chooses a durable location, but the training code still has to save and load checkpoints correctly. `max_restarts` permits Determined to restart the trial; it does not make an arbitrary script resume its training state.

Useful operations:

```bash
det experiment describe <experiment-id>
det experiment pause <experiment-id>
det experiment activate <experiment-id>
det experiment cancel <experiment-id>
```

Design training to resume from shared checkpoints. A container restart must not require files that existed only inside the previous container.

## Shell cleanup policy

The current shell watchdog is based on sustained GPU utilization, not keyboard activity. A shell that stays below the configured threshold can be warned and later stopped; timing is approximate rather than a deadline. See the [Interactive Shell cleanup policy](Interactive_Shell.md#shell-cleanup-policy). Save work continuously to shared storage and use an experiment for long unattended work.

## Related pages

- [Interactive Shell](Interactive_Shell.md)
- [Canonical MCP agent workflow](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.md)
- [Custom Containerized Environment](Custom_Containerized_Environment.md)
- [Cluster Getting Started](Getting_started.md)
- [Cluster Reference](Cluster_Reference.md)
