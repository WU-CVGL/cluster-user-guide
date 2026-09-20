# Getting started with the cluster

[English](Getting_started.md) | [简体中文](Getting_started.zh.md)

This page covers the shortest path from a new account to an SSH login. For storage, Determined, containers, or less common access methods, follow the linked guides at the end.

For agent-assisted cluster work and the Determined MCP service, see the canonical [agent workflow](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.md) and [installation guide](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/README.md).

## 1. Request the accounts you need

Ask the cluster administrator for:

- a Linux account on the login node;
- a Determined account;
- Harbor or other service accounts required by your work;
- your assigned directory and current storage policy.

Do not send passwords or private keys in tickets, chat, source repositories, or task configuration.

## 2. Connect to the campus network

Connect through the campus network or the university VPN. Use the current VPN instructions supplied by the university. If internal names do not resolve, add these client-side hosts entries:

```text
10.0.1.67 login.cvgl.lab
10.0.1.68 cvgl.lab gpu.cvgl.lab harbor.cvgl.lab grafana.cvgl.lab pan.cvgl.lab frp.cvgl.lab wandb.cvgl.lab
```

These addresses are for campus/VPN clients. Service containers may resolve the same names to different internal addresses. If the client entries stop working, confirm the route and current addresses with the administrator.

To edit the hosts file:

- Windows: run Notepad as Administrator and open `C:\Windows\System32\drivers\etc\hosts`.
- Linux: edit `/etc/hosts` with `sudo`.
- macOS: edit `/etc/hosts` with `sudo`, then flush the DNS cache if necessary.

For service URLs, see [Cluster reference](Cluster_Reference.md#services). More network options are in [Network and remote access](Network_and_Remote_Access.md).

## 3. Enroll the cluster CA when required

The login node already has the certificate installed, so skip this step there. On your own device, download [cvgl.crt](https://cvgl.lab/cvgl.crt) and install it using the instructions below. No administrator fingerprint check is required.

If your device cannot download it because the CA is not trusted yet, use this command for the initial download (on Windows, use `curl.exe`):

```bash
curl -k --fail --output cvgl.crt https://cvgl.lab/cvgl.crt
```

Use `-k` only for this initial CA download. After installation, use normal TLS verification.

- Windows, in an elevated PowerShell:

  ```powershell
  Import-Certificate -FilePath .\cvgl.crt -CertStoreLocation Cert:\LocalMachine\Root
  ```

- macOS:

  ```bash
  sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain cvgl.crt
  ```

- Ubuntu/Debian:

  ```bash
  sudo cp cvgl.crt /usr/local/share/ca-certificates/cvgl.crt
  sudo update-ca-certificates
  ```

Configure an application-specific CA path only if that application still reports a certificate error after installation.

## 4. Create a per-device SSH key

Use a separate key pair on each computer and protect it with a strong passphrase:

```bash
ssh-keygen -t ed25519 -f "$HOME/.ssh/id_ed25519_cvgl_cluster"
```

Never copy or share the private key. Only the `.pub` file belongs on the login node.

## 5. Configure a stable SSH alias

Add a host block to `~/.ssh/config`. Replace `YOUR_USERNAME`; confirm the current hostname and port with the administrator if the example does not connect.

```sshconfig
Host cvgl-login
  HostName login.cvgl.lab
  Port 22332
  User YOUR_USERNAME
  IdentityFile ~/.ssh/id_ed25519_cvgl_cluster
  IdentitiesOnly yes
  ForwardAgent no
```

On Windows OpenSSH, `~/.ssh/config` and forward-slash paths work in PowerShell. GUI clients such as MobaXterm or PuTTY need the same host, port, username, and key configured in their session settings.

On first connection, OpenSSH asks to save the host key in `known_hosts`. If it later reports a changed host key, investigate the change before reconnecting. SSH host keys are separate from the HTTPS certificate installed above.

## 6. Install the public key

On Linux and macOS, include the non-default SSH port:

```bash
ssh-copy-id -p 22332 \
  -i "$HOME/.ssh/id_ed25519_cvgl_cluster.pub" \
  YOUR_USERNAME@login.cvgl.lab
```

After the alias is configured, this equivalent form also uses its port and user:

```bash
ssh-copy-id -i "$HOME/.ssh/id_ed25519_cvgl_cluster.pub" cvgl-login
```

Windows OpenSSH normally lacks `ssh-copy-id`. In PowerShell, append the public key over an authenticated SSH connection:

```powershell
Get-Content -Raw "$HOME\.ssh\id_ed25519_cvgl_cluster.pub" |
  ssh -p 22332 YOUR_USERNAME@login.cvgl.lab `
    "umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys"
```

If the account or server policy blocks this method, ask the administrator to install the public key. Do not send the private key.

## 7. Load the key into an SSH agent

On Linux or other Unix-like systems, reuse an existing agent. Start one only when the current environment has no socket:

```bash
if [ -z "${SSH_AUTH_SOCK:-}" ]; then
  eval "$(ssh-agent -s)"
fi
ssh-add "$HOME/.ssh/id_ed25519_cvgl_cluster"
ssh-add -l
```

On macOS, Apple's system `ssh-add` can store the key passphrase in Keychain:

```bash
/usr/bin/ssh-add --apple-use-keychain "$HOME/.ssh/id_ed25519_cvgl_cluster"
```

On macOS versions older than Monterey, Apple's equivalent option is `-K`.

The macOS host block may also include:

```sshconfig
  IgnoreUnknown UseKeychain
  AddKeysToAgent yes
  UseKeychain yes
```

On Windows, start the built-in **OpenSSH Authentication Agent** service from an elevated PowerShell:

```powershell
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
```

Then load the key from a normal user PowerShell:

```powershell
ssh-add "$HOME\.ssh\id_ed25519_cvgl_cluster"
ssh-add -l
```

Do not enable agent forwarding unless the administrator has given a specific, reviewed reason.

## 8. Verify access

```bash
ssh cvgl-login
```

After login, confirm your identity and assigned directories before copying data:

```bash
id
pwd
```

Do not run heavy computation on the login node. Use it for access, file management, and lightweight setup; submit compute through Determined.

## Next steps

- [Shared storage](Shared_Storage.md)
- [Network and remote access](Network_and_Remote_Access.md)
- [Determined AI user guide](Determined_AI_User_Guide.md)
- [Custom containerized environments](Custom_Containerized_Environment.md)
- [Troubleshooting](Troubleshooting.md)
- [Home](../README.md)
