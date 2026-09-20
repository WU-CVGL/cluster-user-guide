<a id="self-hosted-wb"></a>
# 自托管 W&B

[English](Weights_and_Biases.md) | [简体中文](Weights_and_Biases.zh.md)

[首页](../README.zh.md) · [运行任务](Determined_AI_User_Guide.zh.md)

CVGL 提供自托管 Weights & Biases 服务，用于实验跟踪和可视化。用户名、密码和 API token 均向管理员获取。下面命令中的 `local-xxxx` 是 token 占位符，并非可直接使用的凭据。

<a id="access-from-the-campus-network"></a>
## 校园网访问

在校园网设备上，按照[对应平台的操作方法](Getting_started.zh.md#2-connect-to-the-campus-network)添加 hosts 条目：

```text
10.0.1.68 wandb.cvgl.lab
```

浏览器访问 [https://wandb.cvgl.lab/](https://wandb.cvgl.lab/)，也可以直接使用 [http://10.0.1.68:8081](http://10.0.1.68:8081)。域名 HTTPS 入口使用[入门指南](Getting_started.zh.md#3-enroll-the-cluster-ca-when-required)中介绍的集群证书。

在已安装项目所需 W&B SDK 的环境中执行 CLI 登录：

```bash
wandb login --relogin --host=http://10.0.1.68:8081 local-xxxx
```

<a id="access-from-cluster-nodes"></a>
## 集群节点访问

在集群计算节点及其任务容器内，使用 **100G LAN** 地址 `http://192.168.233.8:8081`：

```bash
wandb login --relogin --host=http://192.168.233.8:8081 local-xxxx
```

根据 CLI 或训练进程实际运行的位置选择地址。校园网设备上的浏览器仍可使用校园网入口，查看集群任务产生的结果。

<a id="configure-training-and-agent-workflows"></a>
## 配置训练与 agent 工作流

在实际运行训练的环境中设置服务地址。集群任务使用：

```bash
export WANDB_BASE_URL=http://192.168.233.8:8081
```

如果进程运行在校园网中的个人设备上，则使用 `http://10.0.1.68:8081`。`WANDB_BASE_URL` 指定自托管服务，非交互任务可以通过 `WANDB_API_KEY` 提供 API token。详见官方[登录参考](https://docs.wandb.ai/models/ref/cli/wandb-login)和[环境变量参考](https://docs.wandb.ai/models/track/environment-variables)。

在个人电脑或登录节点上完成登录，不会自动让新任务容器获得认证。通过项目的凭据配置，将凭据提供给任务运行环境。不要将实际 token 提交到仓库，或写入 agent 提示词、任务元数据和报告；向 agent 提供凭据引用即可。上面的 `local-xxxx` 命令用于说明登录语法。

启动工作负载后，检查运行记录和预期指标是否出现在此自托管实例中。代码、数据集和需要保留的输出文件仍放在[共享存储](Shared_Storage.zh.md)，W&B 用于补充实验跟踪。
