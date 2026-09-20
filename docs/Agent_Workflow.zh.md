<a id="use-the-cluster-through-mcp"></a>
# 通过 MCP 使用集群

[English](Agent_Workflow.md) | [简体中文](Agent_Workflow.zh.md)

[首页](../README.zh.md) · [任务类型选择](Determined_AI_User_Guide.zh.md)

推荐将你的 agent 接入 [Determined Cluster MCP](https://github.com/WU-CVGL/determined_cluster_mcp)，处理日常集群任务。该服务通过本地 stdio MCP 提供确定性的存储和计算工具。任何能够启动并使用本地 stdio MCP 服务的客户端或 agent 都可以遵循本工作流；手动操作仍可使用原生 CLI。

MCP 的任务和存储工具不依赖 Codex、GPT 或任何其他模型家族。模型由 MCP 客户端自行选择，可以是 Claude、Grok 或其他模型。模型名称不表示对应厂商的 UI 一定能够启动本地 stdio MCP 服务；请确认你计划使用的客户端具备这一能力。

Agent 应先阅读 [AGENTS.zh.md](../AGENTS.zh.md)，再阅读本工作流及相关任务页面。仓库名为 `determined_cluster_mcp`，可执行程序仍为 `determined-compute` 和 `determined-compute-mcp`。

人工交互式数据探索和可视化也可以使用原生 Determined 的 [Jupyter 工作流](Jupyter_Notebooks.zh.md)。当前 MCP 不接受 `kind: notebook`，不要通过 `compute_launch` 提交 Notebook 任务。

<a id="give-the-agent-a-task"></a>
## 向 agent 描述任务

说明目标和成功判据。如果已经明确，也请提供共享项目路径、代码版本、输入和输出路径、偏好的镜像、资源池及 GPU 数量。Agent 可以复用已有项目配置，仅询问缺失的必要信息。提供凭据文件路径或 SSH 别名，不要提供凭据值。

例如：

> 阅读集群用户指南，使用已连接的 Determined Cluster MCP 评估共享项目中的检查点。复用项目中配置的镜像和资源池，申请一张 GPU，避免排队。先检查文件和容量，规划一个名称有意义的 command 任务，然后提交并跟踪日志。将结果写入共享输出目录，报告任务 ID、退出状态和预期指标文件是否存在。缺少必要路径或设置时再询问我。

<a id="connect-the-service"></a>
## 连接服务

使用当前仓库地址：

```bash
git clone https://github.com/WU-CVGL/determined_cluster_mcp.git
cd determined_cluster_mcp
```

按照服务的[安装指南](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/README.zh.md)配置。在 MCP 客户端中设置可执行程序、配置文件和数据库的绝对路径、owner 命名空间及凭据文件路径。凭据保存在凭据文件或受支持的凭据后端中，不要将值写入提示词、任务名称或工具参数。

计算配置描述集群计算节点上的路径及其容器映射。可选的存储访问配置描述 MCP 服务如何通过本地路径或登录节点访问这些目录。客户端不需要本地 NFS 挂载。SSH 认证代理、macOS Keychain、密码、系统 keyring 和 ControlMaster 复用的配置见[存储访问参考](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/shared-storage-access.zh.md)。

依赖 SSH 认证代理时，MCP 进程必须继承可用的 `SSH_AUTH_SOCK`。使用 ControlMaster 时，其 socket 必须位于同一机器且对 MCP 进程可访问。调用 MCP 工具不需要全局安装 skill。

客户端 agent 可以自行规划并直接调用下文的确定性工具，不需要 `compute_consult`。如果服务配置了可选咨询 worker，它是独立的服务端只读扩展，无法执行需要凭据的存储传输或提交任务；它可用的后端也不决定 MCP 客户端使用哪个模型。

<a id="run-a-workload"></a>
## 运行任务

1. 选择有意义的 `name` 和 `description`、合适的任务类型以及[共享存储](Shared_Storage.zh.md)中的项目目录。确认镜像和资源需求。
2. 需要准备文件时，先调用 `storage_check`，再用 `dry_run: true` 预览 `storage_sync`。检查路径和排除规则后，以 `dry_run: false` 执行。已有文件就绪时无需传输。
3. 针对目标资源池和槽位数调用 `compute_resources`。除非明确希望排队，否则保持 `allow_queue: false`。零槽位 command 使用辅助容器容量，同样需要检查。
4. 调用 `compute_plan`，检查解析后的挂载、工作目录、镜像和任务配置。规划是离线操作，不会查询实时容量、远程文件是否存在或访问权限。
5. 使用稳定的 `request_id` 调用 `compute_launch`。保存返回的本地 `task_id` 和远端 ID。重试相同请求时使用同一个请求 ID；接受状态不确定时，先调查已有记录，再考虑创建另一任务。
6. 使用 `compute_status` 和 `compute_logs` 跟踪任务。报告成功前检查退出信息，以及预期的共享文件或指标。需要本地副本时，先预览再执行 `storage_fetch`；使用 `compute_cancel` 停止不再需要的运行中任务。

服务会在新任务提交前再次检查容量。检查结果是快照，不是资源预留，仍可能遇到调度竞争。被拒绝后，不要擅自切换资源池或允许排队。

<a id="paths-and-persistence"></a>
## 路径与持久化

存储工具的 `shared_dir` 等共享路径参数，以及任务的 `workdir`、`output_dir`，使用计算配置中的**容器路径空间**。服务先将存储操作转换为集群宿主机路径，再通过本地或 SSH 后端访问。`local_dir` 位于运行 MCP 服务的机器上，它可能与显示聊天界面的机器不同。

代码、数据和输出保存在共享存储中。不要将源码目录或归档上传给 Determined。配置中的 `read_only: true` 会禁止服务执行写操作，这是对文件系统权限的补充。只读数据集可以读取或下载，工作目录、上传目标和输出目录必须可写。

本地 SQLite 数据库记录 owner、任务身份和重试、核对状态；共享输出独立于该数据库。使用相同数据库和 owner 的客户端可以看到相同的本地任务记录。Owner 名称是命名空间，不是身份认证边界。

工具参数和错误处理以[服务参考（英文）](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.md)及已连接服务实际提供的工具为准。只报告观察到的结果；提交成功本身不能证明任务已成功完成。
