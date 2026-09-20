<a id="cluster-reference"></a>
# 集群参考

[English](Cluster_Reference.md) | [简体中文](Cluster_Reference.zh.md)

[首页](../README.zh.md)

<a id="services"></a>
## 服务

打开以下内部服务前，请先完成[网络与证书设置](Getting_started.zh.md)。

| 服务 | 用途 |
| --- | --- |
| [集群门户](https://cvgl.lab/) | 服务发现 |
| [Determined](https://gpu.cvgl.lab/) | 任务调度、日志和生命周期管理 |
| [Harbor](https://harbor.cvgl.lab/) | 容器镜像 |
| [Grafana](https://grafana.cvgl.lab/) | 利用率、监控和告警 |
| [Nextcloud](https://pan.cvgl.lab/) | 文件共享 |
| [Weights & Biases](https://wandb.cvgl.lab/) | 实验跟踪；[校园网和 100G LAN 接入](Weights_and_Biases.zh.md) |
| [FRP](https://frp.cvgl.lab/) | 由管理员管理的端口转发 |

请使用自己的账号，并且只申请工作所需的服务。共享链接和凭据应向管理员获取，不要从公开示例中取用。

<a id="how-the-components-fit-together"></a>
## 各组件如何协同工作

你的计算机通过登录节点访问文件，并通过 Determined 调度任务。Determined 在计算节点上启动容器。容器只能通过配置的绑定挂载看到共享存储。Harbor 提供镜像；Grafana 监控资源使用情况。看门狗使用 Grafana 告警回收空闲 shell。

登录节点、你的计算机和任务容器分别拥有独立的文件系统和身份验证上下文。SSH 连接成功并不意味着同时获得 Determined 或 Harbor 的访问权限。两台机器上出现相同的路径字符串，也不能证明它们共享同一个文件系统。

<a id="resource-and-storage-inventory"></a>
## 资源与存储清单

调度决策应以 Determined 的实时资源池和 agent 清单为准。资源池名称、健康 agent、已分配 slot 和辅助容器容量都可能独立变化。[任务提交](Determined_AI_User_Guide.zh.md)说明了相关检查。

有关已配置的存储系列，请参阅[共享存储](Shared_Storage.zh.md)；有关静态设备参考，请参阅[硬件清单](Hardware_Inventory.zh.md)。这两个页面都不保证当前挂载健康状况、可用容量或备份覆盖范围。

<a id="configuration-sources"></a>
## 配置来源

集群运行 Determined **0.38.1**。请使用任务指南中与之匹配的 CLI 版本，并在 master 升级后更新配置的版本。

- [cluster-setup](https://github.com/WU-CVGL/cluster-setup) 包含基础设施定义，其中包括挂载、Determined 配置和看门狗代码。已部署的检出版本可能包含尚未推送到该仓库的更改。
- [determined-compute](https://github.com/WU-CVGL/determined_cluster_mcp) 维护计算 CLI、MCP 服务及其配置参考。
- 本指南维护用户工作流程。部署相关说明应与对应的服务配置保持一致。

Shell 策略记录在[交互式 shell](Interactive_Shell.zh.md)中。Docker/Harbor 兼容流程记录在[容器环境](Custom_Containerized_Environment.zh.md)中。
