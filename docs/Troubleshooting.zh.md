[English](Troubleshooting.md) | [简体中文](Troubleshooting.zh.md)

<a id="troubleshooting"></a>
# 故障排查

接入 [Determined Cluster MCP](https://github.com/WU-CVGL/determined_cluster_mcp) 的 agent 可以协助检查任务状态、日志和存储。提供失败的步骤和脱敏错误；服务设置与任务处理见 [agent 工作流](Agent_Workflow.zh.md)。

[首页](../README.zh.md)

从失败所在层开始排查。记录任务 ID、相关命令和经过脱敏的错误；不要包含密码、token、私钥或完整环境变量转储。

| 现象 | 检查项 |
| --- | --- |
| 无法解析或访问内部主机名 | 检查校园网/VPN 连接和 [hosts 条目](Getting_started.zh.md)。从实际运行客户端的机器测试对应服务。 |
| SSH 失败，或 ControlMaster socket 拒绝连接 | 交互式测试已配置的 SSH alias。Socket 文件可能比连接存活更久；用 `ssh -O check ALIAS` 检查 master。启动自动化前核验 host key 和认证。 |
| 终端里的 SSH 正常，但 MCP 中失败 | 确认 MCP 进程能访问相同的 SSH 配置、已知主机记录、密钥或 ControlMaster socket。若使用 SSH 认证代理，检查 MCP 进程继承的 `SSH_AUTH_SOCK`。 |
| HTTPS 报告未知证书颁发机构 | 登录节点已安装证书。个人设备从[集群证书地址](https://cvgl.lab/cvgl.crt)下载 `cvgl.crt`，按照[安装步骤](Getting_started.zh.md#3-enroll-the-cluster-ca-when-required)配置。如果只有某个应用仍然失败，再为该应用设置 CA 路径。 |
| `docker pull` 正常，但 Buildx 在 `/service/token` 报告 `x509` 错误 | 除 Docker daemon 外，Buildx 客户端也需要 CA。登录节点上，在构建命令前加 `SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab`；参阅 [Buildx 配置](Buildx_and_Harbor.zh.md)。 |
| 独立 builder 无法解析 `harbor.cvgl.lab` | builder 的 registry 解析器需要集群主机名映射。按[独立 builder 配置](Buildx_and_Harbor.zh.md)处理；构建命令的 `--add-host` 或 `--network` 只影响构建步骤，不影响该解析器。 |
| GPU 利用率很低，但任务一直排队 | 检查所选资源池中已启用、非 draining 的 agent 和未分配 slot。利用率不等于分配状态。重新评估请求；若不希望排队，则停止任务。 |
| MCP 报告容量不足或未知 | 检查 `compute_resources`；稍后重试，或在审查需求后显式选择另一个合适资源池。不要反复创建新请求，也不要静默启用排队。 |
| 登录节点上存在某路径，但任务内不存在 | 检查计算节点的 host mount、任务的 `bind_mounts` 和容器路径。检查任务用户权限。使用绝对路径；`/run/determined/workdir/` 不是强制的挂载前缀。 |
| 任务结束后文件消失 | 检查文件是否写入临时容器文件系统。任务执行期间，应持续将需要保留的内容写入已配置的共享挂载。 |
| Shell 被回收 | 阅读[空闲策略](Interactive_Shell.zh.md)。检查告警/通知和共享输出，然后启动新 shell 并重连。保持 SSH 连接或运行 tmux 不会使 shell 获得豁免。 |
| 原生 Notebook 任务在空闲期间被停止 | 长时间空闲的 Notebook 任务目前由管理员手动停止。将 Notebook 和结果保存在共享存储中，需要时重新启动任务；参阅 [Jupyter](Jupyter_Notebooks.zh.md)。 |
| rsync 传输中途失败 | 重试前检查错误和目标目录。失败的传输可能已复制部分文件。修复权限或存储配置，然后重新检查一次新的 preview。 |
| 启动超时 | 再次提交前查找已有本地 task/request。使用 MCP 时，复用完全相同的 request ID；接受结果不确定时使用 reconcile。 |

如果应用需要显式 CA 路径，原生 `det` 支持 `DET_MASTER_CERT_FILE`；`determined-compute` 使用 `--verify-ssl` 和 Python Requests 的 `REQUESTS_CA_BUNDLE`。在实际发出请求的进程环境中，将对应变量指向下载的 `cvgl.crt`。

如需协助，请提供任务类型和 ID、资源池、镜像引用、相关路径映射、失败时间和简短的脱敏日志片段。管理员随后即可检查对应服务，而不需要你的凭据。
