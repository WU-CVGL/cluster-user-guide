# Self-hosted W&B

[English](Weights_and_Biases.md) | [简体中文](Weights_and_Biases.zh.md)

[Home](../README.md) · [Running tasks](Determined_AI_User_Guide.md)

CVGL provides a self-hosted Weights & Biases service for experiment tracking and visualization. Obtain your username, password and API token from the administrator. In the commands below, `local-xxxx` is a placeholder for that token, not a usable credential.

## Access from the campus network

On a campus-network computer, add this hosts entry using the [platform-specific instructions](Getting_started.md#2-connect-to-the-campus-network):

```text
10.0.1.68 wandb.cvgl.lab
```

Open [https://wandb.cvgl.lab/](https://wandb.cvgl.lab/) in a browser, or use [http://10.0.1.68:8081](http://10.0.1.68:8081) directly. The domain-based HTTPS entry uses the cluster certificate described in [Getting started](Getting_started.md#3-enroll-the-cluster-ca-when-required).

Run the CLI in an environment with the project's W&B SDK installed:

```bash
wandb login --relogin --host=http://10.0.1.68:8081 local-xxxx
```

## Access from cluster nodes

On cluster compute nodes and inside their task containers, use the **100G LAN** endpoint, `http://192.168.233.8:8081`:

```bash
wandb login --relogin --host=http://192.168.233.8:8081 local-xxxx
```

Choose the endpoint according to where the CLI or training process runs. A browser on your campus-network computer can continue using the campus address to view results produced by cluster tasks.

## Configure training and agent workflows

Set the base URL in the environment that actually runs training. For a cluster task:

```bash
export WANDB_BASE_URL=http://192.168.233.8:8081
```

For a process running on your campus-network computer, use `http://10.0.1.68:8081` instead. `WANDB_BASE_URL` selects the self-hosted server, and `WANDB_API_KEY` can supply the API token for non-interactive jobs. See the official [login reference](https://docs.wandb.ai/models/ref/cli/wandb-login) and [environment-variable reference](https://docs.wandb.ai/models/track/environment-variables).

A login on your laptop or login node does not automatically authenticate a new task container. Make the credentials available in that task's runtime through your project's secret configuration. Do not commit the actual token or place it in agent prompts, task metadata or reports; give agents a credential reference. The `local-xxxx` commands above illustrate the login syntax.

After starting your workload, check that its run and expected metrics appear in this self-hosted instance. Keep code, datasets and required output files on [shared storage](Shared_Storage.md); W&B tracking complements that workflow.
