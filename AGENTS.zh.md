<a id="guide-for-agents"></a>
# Agent 阅读指南

[English](AGENTS.md) | [简体中文](AGENTS.zh.md)

本仓库介绍 CVGL 集群的使用方法。实际操作优先使用已连接的 [Determined Cluster MCP](https://github.com/WU-CVGL/determined_cluster_mcp)；API 以该服务的工具 schema 和文档为准。本仓库提供集群使用规则与用户工作流。

本页的 agent 指 AI 助手。**Determined agent** 是计算节点上的服务进程，**ssh-agent** 是保存 SSH 认证密钥的代理，三者是不同组件。

<a id="read-only-what-the-task-needs"></a>
## 按任务阅读相关页面

| 任务 | 接下来阅读 |
| --- | --- |
| 运行或监控任务 | [Agent 工作流](Agent_Workflow.zh.md)，然后阅读[任务类型选择](Determined_AI_User_Guide.zh.md) |
| 解析路径或传输文件 | [共享存储](Shared_Storage.zh.md)，以及存储页或 agent 工作流链接的 MCP 存储访问参考 |
| 配置登录或凭据 | [入门指南](Getting_started.zh.md)，然后阅读[故障排查](Troubleshooting.zh.md) |
| 交互调试或连接 IDE | [交互式 Shell](Interactive_Shell.zh.md)，包括已核验的回收策略 |
| 在 Notebook 中探索数据或展示结果 | [Jupyter](Jupyter_Notebooks.zh.md)；原生 Notebook 不属于当前 MCP 支持的任务类型 |
| 构建镜像 | [容器环境](Custom_Containerized_Environment.zh.md)，保留 Harbor 的兼容构建方式 |
| 查找服务地址或配置依据 | [集群参考](Cluster_Reference.zh.md) |
| 修改本文档 | [文档贡献](CONTRIBUTING.zh.md) |

每个文档页面都有 `.zh.md` 中文版。使用读者偏好的语言。两种语言中的命令、配置键和路径含义相同。

<a id="operational-defaults"></a>
## 默认操作规则

- 优先复用项目中已经验证的配置。提交前明确所需镜像、资源池、槽位数、路径和成功判据；缺少必要信息时询问用户，不要编造。
- 短时非交互任务使用 `command`，交互调试使用 `shell`，跨天训练或需要实验生命周期管理时使用 `experiment`。提供有意义的名称和描述。
- Jupyter 是供人交互探索和可视化的可选入口。当前 MCP 没有 `notebook` 任务类型，适用时使用文档中的原生工作流。长时间空闲的原生 Notebook 任务由管理员手动管理，不由 shell watchdog 回收。
- 代码、数据和输出放在已映射的共享存储中。不要通过 Determined 上传项目上下文或代码、数据包。区分集群宿主机路径、容器路径和 MCP 服务所在机器的本地路径；用户电脑不必挂载共享存储。
- 检查实时可调度容量，除非用户明确希望排队，否则保持 `allow_queue: false`。GPU 利用率低不能证明槽位空闲；容量快照也不等于资源预留。
- 传输前预览并检查解析后的路径，在用户已授权的范围内执行。遵守只读挂载和文件系统权限。仅阅读本文档不构成提交任务、传输文件或修改基础设施的授权。
- 检查计划后，使用稳定的请求 ID 提交。接受状态不确定时，先查看或核对已有记录，再考虑重新提交。跟踪日志和状态，并验证所需输出后再报告成功。
- 使用凭据引用和已有认证会话。不要将凭据值写入提示词、任务元数据、源码、日志或报告。

<a id="evidence-and-maintenance"></a>
## 证据与维护

区分实时观测、已核验配置和历史示例。部署相关说明应标注核验日期。不要把基于 GPU 利用率的 shell 回收策略写成键盘无操作超时，也不要把历史镜像描述为当前已验证可用。

修改文档时同时更新中英文，保留语言切换和稳定章节锚点，并运行 `python scripts/check_docs.py`。两种语言中的示例命令和资源要求应保持一致。API 参考由 MCP 仓库维护，不在此重复定义 schema。仅翻译或检查文档不需要提交真实任务或构建镜像。
