<a id="cvgl-cluster-user-guide"></a>
# CVGL 集群用户指南

[English](README.md) | [简体中文](README.zh.md)

在 GPU 集群上运行任务，将代码、数据集、检查点和结果保存在共享存储中。

**推荐使用 [Determined Cluster MCP](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/README.zh.md) 完成 agent 辅助的集群工作。** 请遵循其中的规范 [agent 工作流](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.zh.md)和 [agent 操作指南](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/AGENTS.zh.md)。本仓库维护 CVGL 专用策略、原生 Determined 操作、共享存储、网络接入和开发工具说明。

1. [连接集群](docs/Getting_started.zh.md)：申请账号，配置网络、证书和 SSH。
2. [准备共享存储](docs/Shared_Storage.zh.md)：选择项目目录、传输文件并配置容器挂载。
3. [运行任务](docs/Determined_AI_User_Guide.zh.md)：检查可用容量，选择镜像，为任务起一个有意义的名称并提交。
4. 检查日志和共享目录中的输出，完成后释放资源。

| 需求 | 入口 |
| --- | --- |
| 让 agent 准备、运行并跟踪任务 | [规范 MCP 工作流——推荐](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.zh.md) |
| 一次性脚本、评估和非交互式调试 | [Command 任务](docs/Determined_AI_User_Guide.zh.md#run-a-short-command) |
| 交互式调试、VS Code 或 PyCharm | [交互式 Shell](docs/Interactive_Shell.zh.md) |
| 数据探索、可视化分析与教学 | [Jupyter——可选](docs/Jupyter_Notebooks.zh.md) |
| 跨天训练、恢复或实验跟踪 | [Experiment 任务](docs/Determined_AI_User_Guide.zh.md#run-a-durable-experiment) |
| 记录指标并对比运行结果 | [自托管 W&B](docs/Weights_and_Biases.zh.md) |
| 构建或复用容器镜像 | [容器环境](docs/Custom_Containerized_Environment.zh.md) |

提交前检查可调度容量，默认避免排队。GPU 利用率低不代表 GPU 尚未分配。Shell 受集群外部空闲回收策略管理，应在整个会话期间持续将工作保存到共享存储。

不要将代码或数据集打包为 Determined 任务上下文上传。容器路径可以是 `/SSD/...` 或其他已配置的挂载路径，不必位于 `/run/determined/workdir/` 下。用户自己的电脑无需挂载集群共享存储。

手动操作可参考任务指南中的原生 CLI 示例。MCP 安装以 [MCP README](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/README.zh.md)为准；API 与配置细节见[计算服务参考](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.zh.md)。

[故障排查](docs/Troubleshooting.zh.md) · [网络与远程访问](docs/Network_and_Remote_Access.zh.md) · [集群参考](docs/Cluster_Reference.zh.md) · [文档贡献](CONTRIBUTING.zh.md)
