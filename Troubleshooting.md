[English](Troubleshooting.md) | [简体中文](Troubleshooting.zh.md)

# Troubleshooting

An agent connected to [Determined Cluster MCP](https://github.com/WU-CVGL/determined_cluster_mcp) can help inspect task status, logs and storage. Share the failing step and sanitized error; follow the [agent workflow](Agent_Workflow.md) for service setup and task handling.

[Home](Home.md)

Start with the failing layer. Record the task ID, relevant command and sanitized error; exclude passwords, tokens, private keys and complete environment dumps.

| Symptom | Check |
| --- | --- |
| Internal hostname cannot be resolved or reached | Campus/VPN connectivity and the [hosts entries](Getting_started.md). Test the specific service from the machine running the client. |
| SSH fails or a ControlMaster socket refuses connections | Test the configured SSH alias interactively. A socket file may outlive its connection; check the master with `ssh -O check ALIAS`. Verify the host key and authentication before starting automation. |
| SSH works in a terminal but not through MCP | Confirm the MCP process can see the same SSH config, known hosts, identity or ControlMaster socket. If using an SSH authentication agent, check the MCP process's inherited `SSH_AUTH_SOCK`. |
| HTTPS reports an unknown certificate authority | The login node already has the certificate. On your own device, download `cvgl.crt` from [the cluster certificate URL](https://cvgl.lab/cvgl.crt) and follow the [installation steps](Getting_started.md#3-enroll-the-cluster-ca-when-required). If one application still fails, configure that application's CA path. |
| `docker pull` works but a build reports an `x509` error | Identify the builder with `docker buildx ls`; follow the [Harbor compatibility procedure](Custom_Containerized_Environment.md). Keep the documented `DOCKER_BUILDKIT=0` path until the alternative has been validated. |
| A task stays queued despite low GPU utilization | Check enabled, non-draining agents and unallocated slots in the selected pool. Utilization is not allocation. Reassess the request or stop it if queuing was unintended. |
| MCP reports insufficient or unknown capacity | Inspect `compute_resources`; retry later, or explicitly select another suitable pool after reviewing requirements. Do not repeatedly create new requests or silently enable queuing. |
| A path exists on the login node but not in the task | Check the compute node's host mount, the task's `bind_mounts` and the container path. Check permissions for the task user. Use absolute paths; `/run/determined/workdir/` is not a required mount prefix. |
| Files disappear after a task ends | Check whether they were written inside the temporary container filesystem. Write persistent work to the configured shared mount throughout the task. |
| A shell was reclaimed | Read the [idle policy](Interactive_Shell.md). Check the alert/notification and shared outputs, then start a new shell and reconnect. Keeping SSH connected or running tmux does not exempt a shell. |
| A native Notebook task was stopped while idle | Long-idle Notebook tasks are currently stopped manually by the administrator. Save notebooks and results on shared storage, then start a new task when needed; see [Jupyter](Jupyter_Notebooks.md). |
| An rsync transfer fails partway through | Inspect the error and destination before retrying. A failed transfer may have copied some files. Correct permissions or storage configuration, then review a fresh preview. |
| A launch times out | Look up the existing local task/request before submitting again. With MCP, reuse the identical request ID and use reconciliation when acceptance is uncertain. |

If an application needs an explicit CA path, native `det` supports `DET_MASTER_CERT_FILE`; `determined-compute` uses `--verify-ssl` and Python Requests' `REQUESTS_CA_BUNDLE`. Point the relevant variable to the downloaded `cvgl.crt` in the environment of the process making the request.

If assistance is needed, provide the task kind and ID, resource pool, image reference, relevant path mappings, time of failure and a short sanitized log excerpt. An administrator can then check the corresponding service without needing your credentials.
