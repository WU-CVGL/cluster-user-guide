[English](Interactive_Shell.md) | [简体中文](Interactive_Shell.zh.md)

<a id="interactive-shells-ides-and-ports"></a>
# 交互式 Shell、IDE 与端口

可通过 [agent 工作流](Agent_Workflow.zh.md)使用 [Determined Cluster MCP](https://github.com/WU-CVGL/determined_cluster_mcp) 规划和管理 shell。本页介绍交互式访问、IDE 连接和 shell 生命周期，也提供手动操作所需的原生 CLI 命令。

Determined shell 是临时的交互式开发环境。它适合检查镜像、复现问题或连接 IDE。需要保留的编辑内容、缓存和调试输出应放在共享存储上。

无人值守的一次性脚本使用 command。长时训练或跨夜工作使用带共享检查点的 experiment。

<a id="start-a-shell"></a>
## 启动 shell

先检查当前调度 slot：

```bash
det slot list
```

检查 [`examples/compute/shell.yaml`](../examples/compute/shell.yaml)，替换其中的占位符，然后启动 shell：

```bash
det shell start --config-file examples/compute/shell.yaml
```

Shell 就绪后，该命令会通过 SSH 连接。若要立即分离并打印 ID：

```bash
det shell start --detach --config-file examples/compute/shell.yaml
```

没有可用 slot 时，原生 `det shell start` 可能进入队列。受维护的 MCP/`determined-compute` 工作流会检查当前容量，默认 `allow_queue: false`；见[智能体工作流](Agent_Workflow.zh.md)。

<a id="reconnect-and-stop"></a>
## 重连与停止

列出自己的 shell 并重新连接：

```bash
det shell list
det shell open <shell-id>
```

其他工具需要底层 SSH 命令时，将其打印出来：

```bash
det shell show-ssh-command <shell-id>
```

`show-ssh-command` 是当前写法。上游已弃用旧的 `show_ssh_command` 别名。

完成后停止 shell：

```bash
det shell kill <shell-id>
```

<a id="vs-code-remote-ssh"></a>
## VS Code Remote SSH

1. 安装 **Remote - SSH** 扩展。
2. 在运行 VS Code 的计算机上执行 `det shell show-ssh-command <shell-id>`。
3. 通过 **Remote-SSH: Add New SSH Host** 添加打印出的命令。
4. 连接新主机，并打开映射后的项目目录，例如 `/run/determined/workdir/home/project`。

生成的命令包含保留的任务密钥和 Determined 的代理命令。新的 shell ID 应生成新的配置项。不要将私钥材料复制到仓库中。

<a id="pycharm"></a>
## PyCharm

1. 使用 `det shell show-ssh-command <shell-id>` 生成 SSH 命令。
2. 将其转换为 OpenSSH 配置项，保留 `ProxyCommand`、identity file 和其他选项。
3. 在 **Settings | Tools | SSH Configurations** 中选择 **OpenSSH config and authentication agent**。
4. 测试连接，随后按需将其用于远程解释器。

PyCharm UI 可能无法表示生成命令中的每个选项，因此 OpenSSH 配置项才是可靠来源。

<a id="forward-a-local-port"></a>
## 转发本地端口

在 `--` 之后传递 SSH 选项。例如，将容器端口 `7007` 转发到同号本地端口：

```bash
det shell open <shell-id> -- -L7007:localhost:7007
```

然后在 shell 内启动服务，使其监听容器 loopback 接口，并在本地打开 `http://localhost:7007`。

也可以在第一次连接时转发端口：

```bash
det shell start --config-file examples/compute/shell.yaml -- -L7007:localhost:7007
```

如果 `7007` 已被占用，请选择未使用的本地端口。只暴露必要端口，不要将未认证服务绑定到公共接口。

<a id="keep-work-recoverable"></a>
## 让工作保持可恢复

- 在映射工作区内编辑代码。
- 将调试产物写入映射输出目录。
- 将容器其他位置安装的软件包和文件视为可丢弃内容。
- 记录复现会话所需的镜像 tag 和代码修订版。
- 将长时训练或跨夜工作迁移到带共享检查点的 experiment。

<a id="shell-cleanup-policy"></a>
## Shell 清理策略

以下清理规则仅适用于 **shell**，衡量容器 GPU 利用率，而不是键盘或 SSH 活动。

- Grafana 每 60 秒评估一次规则。
- 当 shell 映射到的 GPU 最大利用率持续 15 分钟低于 10% 时，进入 alerting 状态。
- Watchdog 在每个整点扫描。第一次匹配时发送警告；如果同一告警在下一个整点仍存在，就停止该 shell。
- 30 分钟 query window 只是读取数据的窗口，不是额外等待时间。
- 此规则不会将 No Data 和查询错误状态视为告警，也不会停止其他 Determined 工作负载类型。

若 GPU 利用率持续偏低，根据评估和整点扫描的相位，警告与清理流程给出的理论停止时间约为 75–135 分钟。这不是严格的两小时超时，也不是保证的截止时间；扫描时机和服务故障都可能改变它。

被停止的 shell 无法重连。请将工作保存在共享存储上，并及时处理警告。无人值守的一次性脚本使用 command；长时训练和跨夜工作使用 experiment。

部署源码由[集群参考](Cluster_Reference.zh.md)链接。应使本说明与 watchdog 和 Grafana 配置保持一致。
