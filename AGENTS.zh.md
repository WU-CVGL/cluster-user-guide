<a id="guide-for-agents"></a>
# Agent 阅读指南

[English](AGENTS.md) | [简体中文](AGENTS.zh.md)

本仓库维护 CVGL 集群策略与原生用户工作流。Determined Cluster MCP 的操作规范以远端的 [agent 指南](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/AGENTS.zh.md)和[通用工作流](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.zh.md)为准；API 与配置由[计算服务参考](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.zh.md)定义。

本页的 agent 指 AI 助手。**Determined agent** 是计算节点上的服务进程，**ssh-agent** 是保存 SSH 认证密钥的代理，三者是不同组件。

<a id="read-only-what-the-task-needs"></a>
## 按任务阅读相关页面

| 任务 | 接下来阅读 |
| --- | --- |
| 通过 MCP 运行或监控任务 | [规范 agent 工作流](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.zh.md)，然后阅读本地[任务类型选择](docs/Determined_AI_User_Guide.zh.md) |
| 安装或配置 MCP | [MCP README](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/README.zh.md)和[计算服务参考](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.zh.md) |
| 通过 MCP 访问共享存储 | 本地[存储布局](docs/Shared_Storage.zh.md)和规范[存储访问参考](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/shared-storage-access.zh.md) |
| 排查 MCP 问题 | [规范 MCP 故障排查](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/troubleshooting.zh.md)，再查看本地[集群故障排查](docs/Troubleshooting.zh.md)中的网络、证书、挂载、Buildx 和原生任务问题 |
| 配置可选 Codex 咨询后端 | [咨询服务参考](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/consultation.zh.md) |
| 配置集群登录或凭据 | [入门指南](docs/Getting_started.zh.md)，然后阅读[集群故障排查](docs/Troubleshooting.zh.md) |
| 交互调试或连接 IDE | [交互式 Shell](docs/Interactive_Shell.zh.md)，包括回收策略 |
| 在 Notebook 中探索数据或展示结果 | 使用原生 Notebook 工作流的 [Jupyter](docs/Jupyter_Notebooks.zh.md) |
| 配置实验跟踪 | [自托管 W&B](docs/Weights_and_Biases.zh.md)；集群任务使用 100G LAN 地址 |
| 构建镜像 | [容器环境](docs/Custom_Containerized_Environment.zh.md)，以及当前的 [Buildx 与 Harbor 配置](docs/Buildx_and_Harbor.zh.md) |
| 查找服务地址或配置依据 | [集群参考](docs/Cluster_Reference.zh.md) |
| 修改本文档 | [文档贡献](CONTRIBUTING.zh.md) |

每个文档页面都有 `.zh.md` 中文版。使用读者偏好的语言。两种语言中的命令、配置键和路径含义相同。

<a id="site-specific-points"></a>
## 集群专用要点

- 集群当前运行 Determined `0.38.1`；原生客户端应使用匹配版本。
- 短时非交互任务使用 `command`，交互调试使用 `shell`，可选的人工交互探索使用原生 `notebook`，长时训练或需要实验生命周期管理时使用 `experiment`。
- 代码、数据和输出放在已映射的共享存储中。不要通过 Determined 上传项目上下文或代码、数据包。用户电脑不必挂载集群共享存储。
- 原生提交前检查调度器实时状态。GPU 利用率低不能证明 slot 空闲，原生 `det` 提交可能进入队列。
- Shell watchdog 依据持续 GPU 利用率，而不是键盘活动。原生 Notebook 任务由管理员另行管理。
- 计算任务使用集群的 W&B 100G LAN 地址。部署专用行为以本地网络、证书、存储、Harbor 和 shell 策略页面为准。

<a id="documentation-maintenance"></a>
## 文档维护

当前容量和状态以实时观测为准，策略以仓库配置为准，旧环境配方仅作为起点。不要把基于 GPU 利用率的 shell 回收策略写成键盘无操作超时。

修改文档时同时更新中英文，保留语言切换和稳定章节锚点，并运行 `python scripts/check_docs.py`。MCP 的安装、操作规范、API 细节和故障排查统一在 `WU-CVGL/determined_cluster_mcp` 维护；本仓库只链接对应的规范文档，不复制内容。
