[English](Troubleshooting.md) | [简体中文](Troubleshooting.zh.md)

# Troubleshooting

This page covers CVGL network, certificates, native Determined tasks, shared storage, Buildx, and shell reclamation. For MCP setup and MCP-specific SSH, capacity, launch, or service errors, use the canonical [MCP troubleshooting guide](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/troubleshooting.md).

[Home](../README.md)

Start with the failing layer. Record the task ID, relevant command and sanitized error; exclude passwords, tokens, private keys and complete environment dumps.

| Symptom | Check |
| --- | --- |
| Internal hostname cannot be resolved or reached | Campus/VPN connectivity and the [hosts entries](Getting_started.md). Test the specific service from the machine running the client. |
| SSH fails or a ControlMaster socket refuses connections | Test the configured SSH alias interactively. A socket file may outlive its connection; check the master with `ssh -O check ALIAS`. Verify the host key and authentication before starting automation. |
| HTTPS reports an unknown certificate authority | The login node already has the certificate. On your own device, download `cvgl.crt` from [the cluster certificate URL](https://cvgl.lab/cvgl.crt) and follow the [installation steps](Getting_started.md#3-enroll-the-cluster-ca-when-required). If one application still fails, configure that application's CA path. |
| `docker pull` works but Buildx reports an `x509` error at `/service/token` | The Buildx client needs the CA as well as the Docker daemon. On the login node, prefix the build command with `SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab`; see the [Buildx setup](Buildx_and_Harbor.md). |
| An independent builder cannot resolve `harbor.cvgl.lab` | Its registry resolver needs the cluster hostname mapping. Follow the [independent-builder setup](Buildx_and_Harbor.md); a build's `--add-host` or `--network` flag only affects build steps, not this resolver. |
| A task stays queued despite low GPU utilization | Check enabled, non-draining agents and unallocated slots in the selected pool. Utilization is not allocation. Reassess the request or stop it if queuing was unintended. |
| A path exists on the login node but not in the task | Check the compute node's host mount, the task's `bind_mounts` and the container path. Check permissions for the task user. Use absolute paths; `/run/determined/workdir/` is not a required mount prefix. |
| Files disappear after a task ends | Check whether they were written inside the temporary container filesystem. Write persistent work to the configured shared mount throughout the task. |
| A shell was reclaimed | Read the [idle policy](Interactive_Shell.md). Check the alert/notification and shared outputs, then start a new shell and reconnect. Keeping SSH connected or running tmux does not exempt a shell. |
| A native Notebook task was stopped while idle | Long-idle Notebook tasks are currently stopped manually by the administrator. Save notebooks and results on shared storage, then start a new task when needed; see [Jupyter](Jupyter_Notebooks.md). |
| An rsync transfer fails partway through | Inspect the error and destination before retrying. A failed transfer may have copied some files. Correct permissions or storage configuration, then review a fresh preview. |

If native `det` needs an explicit CA path, set `DET_MASTER_CERT_FILE` to the downloaded `cvgl.crt` in the environment of that process.

If assistance is needed, provide the task kind and ID, resource pool, image reference, relevant path mappings, time of failure and a short sanitized log excerpt. An administrator can then check the corresponding service without needing your credentials.
