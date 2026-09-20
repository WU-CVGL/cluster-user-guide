<a id="getting-started-with-the-cluster"></a>
# 集群入门

[English](Getting_started.md) | [简体中文](Getting_started.zh.md)

本页介绍从获得新账户到完成 SSH 登录的最短流程。共享存储、Determined、容器以及不常用的访问方式，请参阅文末链接。

如需使用 agent 辅助完成集群工作或使用 Determined MCP 服务，请参阅规范的 [agent 工作流](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.zh.md)和[安装指南](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/README.zh.md)。

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

请通过校园网络或学校 VPN 连接，并使用学校提供的最新 VPN 说明。如果内部域名无法解析，请在客户端添加以下 hosts 条目：

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

登录节点已经安装好证书，可以跳过此步骤。在个人设备上下载 [cvgl.crt](https://cvgl.lab/cvgl.crt)，然后按下面的方式安装即可，无需找管理员核对指纹。

如果设备因尚未信任该 CA 而无法下载，可用以下命令完成首次下载（Windows 使用 `curl.exe`）：

```bash
curl -k --fail --output cvgl.crt https://cvgl.lab/cvgl.crt
```

`-k` 只能用于这次初始 CA 下载。安装后应恢复正常 TLS 验证。

- Windows，在提升权限的 PowerShell 中运行：

  ```powershell
  Import-Certificate -FilePath .\cvgl.crt -CertStoreLocation Cert:\LocalMachine\Root
  ```

- macOS：

  ```bash
  sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain cvgl.crt
  ```

- Ubuntu/Debian：

  ```bash
  sudo cp cvgl.crt /usr/local/share/ca-certificates/cvgl.crt
  sudo update-ca-certificates
  ```

只有应用在安装后仍报告证书错误时，才需要单独为它设置 CA 路径。

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

首次连接时，OpenSSH 会询问是否将主机密钥保存到 `known_hosts`。如果后续提示主机密钥变化，先查明原因再重新连接。SSH 主机密钥与上面安装的 HTTPS 证书是不同机制。

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
- [首页](../README.zh.md)
