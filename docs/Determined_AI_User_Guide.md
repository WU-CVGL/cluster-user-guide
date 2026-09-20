[English](Determined_AI_User_Guide.md) | [简体中文](Determined_AI_User_Guide.zh.md)

# Determined AI: practical user guide

For routine work, use the [agent workflow](Agent_Workflow.md) with [Determined Cluster MCP](https://github.com/WU-CVGL/determined_cluster_mcp). This page explains task selection and provides native CLI commands for manual operation.

Determined runs containerized work on the GPU cluster. Keep the durable parts of every job—source code, datasets, checkpoints, and outputs—on shared storage. Treat the task container as temporary.

## Choose the right workload

| Workload | Use it for | Typical lifetime |
| --- | --- | --- |
| **Command** | Short, non-interactive evaluation, conversion, or preprocessing | Minutes to hours |
| **Shell** | Interactive debugging, IDE access, and environment inspection | While actively debugging |
| **Notebook** (optional, native CLI) | Data exploration, visual analysis and teaching | While actively analyzing |
| **Experiment** | Long or overnight training, checkpointing, restart, and trial tracking | Hours to days |

Use a command by default for one-off work, including short unattended jobs. Use a shell when a person needs to interact with the process. Use an experiment for overnight training or when checkpoint recovery and trial tracking are needed.

[Jupyter](Jupyter_Notebooks.md) is an optional interface for interactive research. Long-idle native Notebook tasks are currently stopped manually by the administrator; the shell watchdog does not manage them. The current MCP compute service does not provide a Notebook task kind.

Give every task a short, meaningful name and a description that says what it runs. Names such as `evaluate-checkpoint-240k` are easier to operate than UUIDs or `test`.

Native command and shell configs expose one `description` field, so put the short display name on its first line and the purpose on following lines. Experiments have separate `name` and `description` fields.

## Install and authenticate

The cluster runs Determined `0.38.1`; install the matching CLI. The login node already has the cluster CA; on your own device, follow the [certificate setup](Getting_started.md#3-enroll-the-cluster-ca-when-required). Set `DET_MASTER_CERT_FILE` to the downloaded `cvgl.crt` only if the CLI still needs an explicit CA path:

```bash
python -m pip install "determined==0.38.1"
export DET_MASTER=https://gpu.cvgl.lab
# If needed: export DET_MASTER_CERT_FILE=/absolute/path/to/cvgl.crt
det user login <username>
```

Match the CLI again when the master is upgraded. See [Cluster Reference](Cluster_Reference.md) for the live service and configuration sources.

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

Do not pass `--context`, `--include`, or a model-directory argument for this workflow. Native `det experiment create CONFIG` accepts an omitted model-definition argument and therefore sends an empty context. The maintained `determined-compute` service also rejects upload contexts.

## Check scheduler capacity

Scheduler slots determine whether a GPU task can start. GPU utilization from `nvidia-smi` does not tell you whether a slot is schedulable.

With the native CLI, inspect current slots and their resource pools:

```bash
det slot list
det slot list --json
```

Count only enabled, non-draining, free slots in the requested pool. Multi-GPU single-node work requires enough free slots on one agent.

The maintained compute service provides a conservative capacity view after its [separate installation and credential setup](Agent_Workflow.md#connect-the-service). It does not reuse a native `det` login session:

```bash
determined-compute \
  --api-url "$DET_MASTER" \
  --verify-ssl --secrets-file /absolute/path/to/credentials.env \
  resources --slots 1 --pool <resource-pool>
```

Its MCP and CLI launch path defaults to `allow_queue: false`, so a new launch is rejected when capacity is busy or unknown. This is a point-in-time check, not a reservation.

The native `det` launch commands do **not** provide the same no-queue guard. Capacity can change between inspection and submission, and a native submission may queue.

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

## Use the maintained compute service and MCP

The maintained `determined-compute` layer adds:

- persistent local task records and idempotent request IDs;
- shared-storage-only path validation;
- meaningful names and descriptions;
- capacity admission with `allow_queue: false` by default;
- owner-scoped status, logs, cancellation, and conservative reconciliation.

For the agent workflow and MCP setup, see [Agent Workflow](Agent_Workflow.md). The service's own documentation is the source of truth for request fields and installation details.

## Shell cleanup policy

The current shell watchdog is based on sustained GPU utilization, not keyboard activity. A shell that stays below the configured threshold can be warned and later stopped; timing is approximate rather than a deadline. See the [Interactive Shell cleanup policy](Interactive_Shell.md#shell-cleanup-policy). Save work continuously to shared storage and use an experiment for long unattended work.

## Related pages

- [Interactive Shell](Interactive_Shell.md)
- [Agent Workflow](Agent_Workflow.md)
- [Custom Containerized Environment](Custom_Containerized_Environment.md)
- [Cluster Getting Started](Getting_started.md)
- [Cluster Reference](Cluster_Reference.md)
