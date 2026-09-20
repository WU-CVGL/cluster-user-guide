<a id="getting-started-with-the-cluster"></a>
# 集群入门

[English](Getting_started.md) | [简体中文](Getting_started.zh.md)

本页介绍从获得新账户到完成经过验证的 SSH 登录的最短流程。共享存储、Determined、容器以及不常用的访问方式，请参阅文末链接。

如需使用智能体辅助完成集群工作或使用 Determined MCP 服务，请参阅[智能体工作流](Agent_Workflow.zh.md)和 [`WU-CVGL/determined_cluster_mcp`](https://github.com/WU-CVGL/determined_cluster_mcp)。

<a id="1-request-the-accounts-you-need"></a>
## 1. 申请所需账户

请向集群管理员申请：

- 登录节点上的 Linux 账户；
- Determined 账户；
- 工作所需的 Harbor 或其他服务账户；
- 分配给你的目录以及当前存储策略。

不要在工单、聊天、源代码仓库或任务配置中发送密码或私钥。

<a id="2-connect-to-the-campus-network"></a>
## 2. 连接校园网络

请通过校园网络或学校 VPN 连接，并使用学校提供的最新 VPN 说明。如果内部域名无法解析，请在客户端添加以下 hosts 条目（已于 2026-09-20 根据部署访问配置核对）：

```text
10.0.1.67 login.cvgl.lab
10.0.1.68 cvgl.lab gpu.cvgl.lab harbor.cvgl.lab grafana.cvgl.lab pan.cvgl.lab frp.cvgl.lab wandb.cvgl.lab
```

这些地址供校园网/VPN 客户端使用。服务容器可能把相同域名解析到不同的内部地址。如果客户端条目失效，请向管理员确认路由和最新地址。

hosts 文件的位置和修改方式：

- Windows：以管理员身份运行记事本，打开 `C:\Windows\System32\drivers\etc\hosts`。
- Linux：使用 `sudo` 编辑 `/etc/hosts`。
- macOS：使用 `sudo` 编辑 `/etc/hosts`，必要时刷新 DNS 缓存。

服务 URL 请参阅[集群参考](Cluster_Reference.zh.md#services)。更多网络选项请参阅[网络与远程访问](Network_and_Remote_Access.zh.md)。

<a id="3-enroll-the-cluster-ca-when-required"></a>
## 3. 按需登记集群 CA

部分内部 HTTPS 服务使用私有证书颁发机构。请通过可信的管理员渠道获取 CA 证书及其 SHA-256 指纹，最好分别通过两个渠道获取。导入前先验证：

```bash
openssl x509 -in cvgl-root-ca.crt -noout -fingerprint -sha256
```

不要为了绕过未知证书而关闭 TLS 验证。

- Windows：把已验证的 CA 导入**受信任的根证书颁发机构**。Git for Windows 可通过 `git config --global http.sslbackend schannel` 使用 Windows 信任存储。
- Ubuntu/Debian：把证书复制到 `/usr/local/share/ca-certificates/cvgl-root-ca.crt`，然后运行 `sudo update-ca-certificates`。
- macOS：使用“钥匙串访问”把证书导入系统钥匙串，并明确设为信任其 SSL 用途。
- 浏览器和容器运行时可能使用各自的信任存储。请按照相应应用的文档添加同一份已验证 CA。

详情请参阅[网络与远程访问](Network_and_Remote_Access.zh.md#internal-ca-certificates)。

<a id="4-create-a-per-device-ssh-key"></a>
## 4. 为每台设备创建独立 SSH 密钥

每台计算机使用不同的密钥对，并使用强口令保护私钥：

```bash
ssh-keygen -t ed25519 -f "$HOME/.ssh/id_ed25519_cvgl_cluster"
```

不要复制或分享私钥。只有 `.pub` 文件应放到登录节点上。

<a id="5-configure-a-stable-ssh-alias"></a>
## 5. 配置稳定的 SSH 别名

在 `~/.ssh/config` 中添加以下主机配置。替换 `YOUR_USERNAME`；如果示例无法连接，请向管理员确认当前主机名和端口。

```sshconfig
Host cvgl-login
  HostName login.cvgl.lab
  Port 22332
  User YOUR_USERNAME
  IdentityFile ~/.ssh/id_ed25519_cvgl_cluster
  IdentitiesOnly yes
  ForwardAgent no
```

在 Windows OpenSSH 中，PowerShell 支持 `~/.ssh/config` 和使用正斜杠的路径。MobaXterm、PuTTY 等 GUI 客户端需要在会话设置中配置相同的主机、端口、用户名和密钥。

接受新的主机密钥前，请与管理员提供的指纹进行比对。主机密钥发生变化时必须停止连接，直到原因得到确认。

<a id="6-install-the-public-key"></a>
## 6. 安装公钥

在 Linux 和 macOS 上，应包含非默认 SSH 端口：

```bash
ssh-copy-id -p 22332 \
  -i "$HOME/.ssh/id_ed25519_cvgl_cluster.pub" \
  YOUR_USERNAME@login.cvgl.lab
```

配置别名后，也可以使用以下等价命令；它会使用别名中的端口和用户：

```bash
ssh-copy-id -i "$HOME/.ssh/id_ed25519_cvgl_cluster.pub" cvgl-login
```

Windows OpenSSH 通常不包含 `ssh-copy-id`。在 PowerShell 中，可通过经过认证的 SSH 连接追加公钥：

```powershell
Get-Content -Raw "$HOME\.ssh\id_ed25519_cvgl_cluster.pub" |
  ssh -p 22332 YOUR_USERNAME@login.cvgl.lab `
    "umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys"
```

如果账户或服务器策略阻止这种方式，请让管理员安装公钥。不要发送私钥。

<a id="7-load-the-key-into-an-ssh-agent"></a>
## 7. 将密钥载入 SSH 认证代理

在 Linux 或其他 Unix 类系统上，请复用已有的 SSH 认证代理。仅当当前环境没有代理 socket 时才启动一个：

```bash
if [ -z "${SSH_AUTH_SOCK:-}" ]; then
  eval "$(ssh-agent -s)"
fi
ssh-add "$HOME/.ssh/id_ed25519_cvgl_cluster"
ssh-add -l
```

在 macOS 上，Apple 系统自带的 `ssh-add` 可以把密钥口令存入钥匙串：

```bash
/usr/bin/ssh-add --apple-use-keychain "$HOME/.ssh/id_ed25519_cvgl_cluster"
```

在早于 Monterey 的 macOS 版本中，Apple 提供的等价选项为 `-K`。

macOS 主机配置还可以包含：

```sshconfig
  IgnoreUnknown UseKeychain
  AddKeysToAgent yes
  UseKeychain yes
```

在 Windows 上，请先在提升权限的 PowerShell 中启动内置的 **OpenSSH Authentication Agent** 服务：

```powershell
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
```

然后在普通用户 PowerShell 中载入密钥：

```powershell
ssh-add "$HOME\.ssh\id_ed25519_cvgl_cluster"
ssh-add -l
```

除非管理员给出了明确且经过审查的理由，否则不要启用 SSH 认证代理转发。

<a id="8-verify-access"></a>
## 8. 验证访问

```bash
ssh cvgl-login
```

登录后，在复制数据之前确认你的身份和分配目录：

```bash
id
pwd
```

不要在登录节点上运行重型计算。登录节点仅用于访问、文件管理和轻量设置；计算任务应通过 Determined 提交。

<a id="next-steps"></a>
## 后续步骤

- [共享存储](Shared_Storage.zh.md)
- [网络与远程访问](Network_and_Remote_Access.zh.md)
- [Determined AI 用户指南](Determined_AI_User_Guide.zh.md)
- [自定义容器环境](Custom_Containerized_Environment.zh.md)
- [故障排查](Troubleshooting.zh.md)
- [首页](Home.zh.md)
