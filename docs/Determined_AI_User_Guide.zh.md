[English](Determined_AI_User_Guide.md) | [简体中文](Determined_AI_User_Guide.zh.md)

<a id="determined-ai-practical-user-guide"></a>
# Determined AI：实用用户指南

Agent 辅助操作请使用规范的 [Determined Cluster MCP 工作流](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.zh.md)。本页说明集群任务类型选择，并提供手动操作所需的原生 CLI 命令。

Determined 在 GPU 集群上运行容器化任务。每个任务中需要持久保存的内容——源代码、数据集、检查点和输出——都应放在共享存储上。任务容器应视为临时环境。

<a id="choose-the-right-workload"></a>
## 选择正确的工作负载类型

| 工作负载 | 适用场景 | 典型持续时间 |
| --- | --- | --- |
| **Command** | 短时、非交互式的评估、转换或预处理 | 数分钟到数小时 |
| **Shell** | 交互式调试、IDE 访问和环境检查 | 主动调试期间 |
| **Notebook**（可选，使用原生 CLI） | 数据探索、可视化分析和教学 | 主动分析期间 |
| **Experiment** | 长时或跨夜训练、检查点恢复和试验跟踪 | 数小时到数天 |

一次性工作默认使用 command，包括短时无人值守任务。需要人工与进程交互时使用 shell。跨夜训练，或需要检查点恢复和试验跟踪时，使用 experiment。

[Jupyter](Jupyter_Notebooks.zh.md) 是交互式研究的可选原生入口。长时间空闲的原生 Notebook 任务目前由管理员手动停止，不由 shell watchdog 管理。MCP 支持的任务类型以规范的[计算服务参考](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.zh.md)为准。

为每个任务设置简短且有意义的名称，并用描述说明它运行什么。`evaluate-checkpoint-240k` 这类名称比 UUID 或 `test` 更便于操作。

原生 command 和 shell 配置只有一个 `description` 字段，因此应在第一行写简短显示名称，后续行说明用途。Experiment 分别提供 `name` 和 `description` 字段。

<a id="install-and-authenticate"></a>
## 安装与认证

集群运行 Determined `0.38.1`；请安装匹配的 CLI。登录节点已安装集群 CA；个人设备请先完成[证书配置](Getting_started.zh.md#3-enroll-the-cluster-ca-when-required)。仅当 CLI 仍需显式 CA 路径时，将 `DET_MASTER_CERT_FILE` 指向下载的 `cvgl.crt`：

```bash
python -m pip install "determined==0.38.1"
export DET_MASTER=https://gpu.cvgl.lab
# If needed: export DET_MASTER_CERT_FILE=/absolute/path/to/cvgl.crt
det user login <username>
```

Master 升级后应再次匹配 CLI 版本。实时服务和配置来源见[集群参考](Cluster_Reference.zh.md)。

启动任务前检查认证：

```bash
det user whoami
```

<a id="put-all-durable-files-on-shared-storage"></a>
## 将所有持久文件放在共享存储上

典型映射如下：

| Host 路径 | 容器路径 | 用途 |
| --- | --- | --- |
| `/workspace/<username>` | `/run/determined/workdir/home` | 代码、检查点和输出 |
| `/datasets` | `/run/determined/workdir/data` | 共享数据集，通常只读 |

启动前：

1. 将确切的代码修订版复制或同步到共享工作区下的目录。
2. 让任务工作目录指向该映射目录。
3. 将结果和检查点写入另一个映射目录。
4. 从共享存储挂载数据集；不要将数据集复制到提交上下文中。

[`examples/compute/`](../examples/compute/) 中的示例采用这一布局。使用前替换所有占位符。

此工作流不要传递 `--context`、`--include` 或模型目录参数。原生 `det experiment create CONFIG` 允许省略模型定义参数，因此会发送空上下文。

<a id="check-scheduler-capacity"></a>
## 检查调度容量

GPU 任务能否启动由调度器 slot 决定。`nvidia-smi` 显示的 GPU 利用率不能说明一个 slot 是否可调度。

使用原生 CLI 检查当前 slot 及其资源池：

```bash
det slot list
det slot list --json
```

只统计目标资源池中已启用、未处于排空（draining）状态且空闲的槽位。单机多 GPU 任务需要同一计算节点的 Determined agent 上有足够的空闲槽位。

原生 `det` 启动命令可能进入队列。容量可能在检查与提交之间变化，因此提交后应检查任务；如果本无意排队，则取消任务。MCP 的容量和准入行为以规范的[计算服务参考](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.zh.md)为准。

<a id="run-a-short-command"></a>
## 运行短时 command

检查 [`examples/compute/command.yaml`](../examples/compute/command.yaml)，然后运行：

```bash
det command run \
  --config-file examples/compute/command.yaml \
  bash -lc 'mkdir -p /run/determined/workdir/home/results && cd /run/determined/workdir/home/project && python scripts/evaluate.py --output /run/determined/workdir/home/results/eval.json'
```

除非指定 `--detach`，该命令会持续输出日志。重新打开日志或停止任务：

```bash
det task logs -f <command-id>
det command kill <command-id>
```

<a id="start-an-interactive-shell"></a>
## 启动交互式 shell

检查 [`examples/compute/shell.yaml`](../examples/compute/shell.yaml)，然后运行：

```bash
det shell start --config-file examples/compute/shell.yaml
```

Shell 用于调试和 IDE 访问。重连、VS Code/PyCharm 设置、端口转发和当前生命周期说明见[交互式 Shell](Interactive_Shell.zh.md)。

<a id="run-a-durable-experiment"></a>
## 运行可恢复的 experiment

检查 [`examples/compute/experiment.yaml`](../examples/compute/experiment.yaml)。它的入口点会进入共享代码目录，检查点存储也位于共享工作区中。

提交时不要提供模型定义目录：

```bash
det experiment create examples/compute/experiment.yaml
```

不要追加 `.` 或其他代码目录，否则会打包并上传文件。Experiment 通过 bind mount 读取代码和数据。

请根据训练程序调整示例。只有当代码向 Determined 报告名称完全相同的指标时，`searcher.metric: validation_loss` 才有意义。`checkpoint_storage` 选择持久存储位置，但训练代码仍须正确保存和加载检查点。`max_restarts` 允许 Determined 重启 trial；它不会让任意脚本自动恢复训练状态。

常用操作：

```bash
det experiment describe <experiment-id>
det experiment pause <experiment-id>
det experiment activate <experiment-id>
det experiment cancel <experiment-id>
```

训练程序应能够从共享检查点恢复。容器重启后，不得依赖只存在于前一个容器中的文件。

<a id="shell-cleanup-policy"></a>
## Shell 清理策略

当前 shell watchdog 依据持续 GPU 利用率，而不是键盘活动。持续低于阈值的 shell 可能先收到警告，随后被停止；时间是近似值，不是截止时间。详见[交互式 Shell 清理策略](Interactive_Shell.zh.md#shell-cleanup-policy)。请持续将工作保存到共享存储，无人值守的长时工作应使用 experiment。

<a id="related-pages"></a>
## 相关页面

- [交互式 Shell](Interactive_Shell.zh.md)
- [规范 MCP agent 工作流](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.zh.md)
- [自定义容器环境](Custom_Containerized_Environment.zh.md)
- [集群入门](Getting_started.zh.md)
- [集群参考](Cluster_Reference.zh.md)
