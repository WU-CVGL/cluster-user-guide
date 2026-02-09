<h1 align="center">Getting started with the cluster</h1>

- [Requesting accounts](#requesting-accounts)
- [Accessing the cluster](#accessing-the-cluster)
  - [Security](#security)
  - [Setting up the hosts file](#setting-up-the-hosts-file)
    - [For Windows](#for-windows)
    - [For Linux, \*nix including macOS](#for-linux-nix-including-macos)
    - [Hosts Modification](#hosts-modification)
  - [Install the root CA certificate (Optional)](#install-the-root-ca-certificate-optional)
  - [SSH](#ssh)
    - [SSH in Linux, \*nix including macOS](#ssh-in-linux-nix-including-macos)
    - [SSH in Windows](#ssh-in-windows)
    - [SSH keys](#ssh-keys)
    - [SSH keys on Linux](#ssh-keys-on-linux)
    - [SSH keys on Windows](#ssh-keys-on-windows)
    - [Safety rules](#safety-rules)
    - [How to use keys with non-default names](#how-to-use-keys-with-non-default-names)
  - [X11 forwarding and remote desktop](#x11-forwarding-and-remote-desktop)
    - [X11 forwarding](#x11-forwarding)
    - [Remote desktop via RDP](#remote-desktop-via-rdp)
- [Data management](#data-management)
  - [Introduction](#introduction)
  - [Uploading and downloading data](#uploading-and-downloading-data)
    - [Uploading](#uploading)
    - [Downloading](#downloading)
    - [Using proxy service](#using-proxy-service)
      - [Self-provisioned services](#self-provisioned-services)
        - [RackNerd US: Los Angeles DC-03 Datacenter, with 12TB/mo **lots of** traffic](#racknerd-us-los-angeles-dc-03-datacenter-with-12tbmo-lots-of-traffic)
        - [Oracle Cloud Japan: Osaka, with 10TB/mo **free** traffic (14 USD/TB beyond)](#oracle-cloud-japan-osaka-with-10tbmo-free-traffic-14-usdtb-beyond)
        - [Bandwagon US: Los Angeles DC1, with 2TB/mo traffic](#bandwagon-us-los-angeles-dc1-with-2tbmo-traffic)
        - [Bandwagon US: Los Angeles DC6, with 1TB/mo **fast** traffic](#bandwagon-us-los-angeles-dc6-with-1tbmo-fast-traffic)
      - [IPLC services](#iplc-services)
        - [IPLC-HK01](#iplc-hk01)
        - [IPLC-HK02](#iplc-hk02)
        - [IPLC-US52](#iplc-us52)
        - [IPLC-US53](#iplc-us53)
        - [jms-iplc-temp-workaround-hk-s01](#jms-iplc-temp-workaround-hk-s01)
        - [jms-iplc-temp-workaround-us-s02](#jms-iplc-temp-workaround-us-s02)
      - [Proxychains](#proxychains)
      - [Any python downloading that uses `urllib`](#any-python-downloading-that-uses-urllib)
      - [Huggingface](#huggingface)
      - [Environment variable](#environment-variable)
    - [Using our aria2 service](#using-our-aria2-service)

# Requesting accounts

Accounts that need to be created by the administrator include:

- A Linux account on the login node (`login.cvgl.lab`)
- An account for the batch system (Determined AI, [gpu.cvgl.lab](https://gpu.cvgl.lab/)).
- An account for Harbor - the container registry ([harbor.cvgl.lab](https://harbor.cvgl.lab/))
- A Nextcloud account ([pan.cvgl.lab](https://pan.cvgl.lab/))

# Accessing the cluster

## Security

Accessing the cluster is currently only possible via secure protocols (ssh, scp, rsync). The cluster is only accessible from inside the campus's local area network. If you would like to connect from a computer, which is not inside the campus's network, then you would need to establish a [VPN](https://vpn.westlake.edu.cn/) connection first.

## Setting up the hosts file

Since our cluster is only accessible inside the campus LAN, and we do not have the administration of the DNS server, setting up the `hosts` file is the best way to translate human-friendly hostnames into IP addresses.

The way to modify the `hosts` file is as follows:

### For Windows

- Press `Win-Key + R`. A small window will pop up.

- Type in the following command and press `Ctrl+Shift+Enter`, to make notepad run as administrator and edit the `hosts` file.

```bat
notepad C:\Windows\System32\drivers\etc\hosts
```

### For Linux, *nix including macOS

- Edit `/etc/hosts` with root privilege in your favorite way. For example:

```bash
sudo vim /etc/hosts
```

### Hosts Modification

Append these lines to the end of the `hosts` file:

```text
10.0.1.67 login.cvgl.lab
10.0.1.68 cvgl.lab
10.0.1.68 frp.cvgl.lab
10.0.1.68 gpu.cvgl.lab
10.0.1.68 grafana.cvgl.lab
10.0.1.68 harbor.cvgl.lab
10.0.1.68 pan.cvgl.lab
10.0.1.68 wandb.cvgl.lab
```

## Install the root CA certificate (Optional)

Since we are using a self-signed certificate, after modifying the host, when we use a web browser to access the service, a security warning appears saying the certificate is not recognized. We can suppress this warning by making the system trust the certificate.

The certificate can be downloaded at: [https://cvgl.lab/cvgl.crt](https://cvgl.lab/cvgl.crt)

- For Windows, right-click the CA certificate file and select 'Install Certificate'. Follow the prompts to add the certificate to the **Trusted Root Certification Authorities**. If you are using Git for Windows, you will need to configure Git to use Windows native crypto backend: `git config --global http.sslbackend schannel`

- For Linux (tested Ubuntu), first, you need the `ca-certificates` package installed, then copy the `.crt` file into the folder `/usr/local/share/ca-certificates`, and update certificates system-wide with the command `sudo update-ca-certificates`. This works for most applications, but browsers like google-chrome and chromium on Linux have their own certificate storage. You need to go to `chrome://settings/certificates`, select "Authorities", and import the `.crt` file. To use our Docker registry `registry.cvgl.lab`, you need to create the folder `/etc/docker/certs.d/registry.cvgl.lab/` and copy ther certificate into it.

## SSH

You can connect to the cluster via the SSH protocol. For this purpose, it is required that you have an SSH client installed. The information required to connect to the cluster is the hostname (which resolves to an IP address) of the cluster and your account credentials (username, password).

Since we have set up the *hosts* in the [previous section](#hosts), we can use the human-readable hostname to make our connection.

| Hostname | IP Address | Port |
| :-- | :-- | :-- |
|login.cvgl.lab|10.0.1.67|22332|

### SSH in Linux, *nix including macOS

Open a terminal and use the standard ssh command

```bash
ssh -p 22332 username@login.cvgl.lab
```

where **username** is your username and the **hostname** can be found in the table shown above. The parameter `-p 22332` is used to declare the SSH port used on the server. For security, we modified the default port. If for instance, user **peter** would like to access the cluster, then the command would be

```text
peter@laptop:~$ ssh -p 22332 peter@login.cvgl.lab
peter@login.cvgl.lab's password:
Welcome to Ubuntu 20.04.4 LTS (GNU/Linux 5.4.0-104-generic x86_64)

* Documentation:  https://help.ubuntu.com
* Management:     https://landscape.canonical.com
* Support:        https://ubuntu.com/advantage

System information as of Tue 15 Mar 2022 11:51:03 AM UTC

System load:  0.0                 Users logged in:          1
Usage of /:   28.0% of 125.49GB   IPv4 address for docker0: 172.17.0.1
Memory usage: 6%                  IPv4 address for enp1s0:  192.168.122.2
Swap usage:   0%                  IPv4 address for enp6s0:  10.0.1.67
Processes:    278

0 updates can be applied immediately.

Last login: Tue Mar 15 11:29:19 2022 from 172.16.29.72
```

Note that when it prompts to enter the password:

```text
peter@login.cvgl.lab's password:
```

there will not be any visual feedback (i.e. asterisks) in order not to show the length of your password.

### SSH in Windows

Since Windows 10, an ssh client is also provided in the operating system, but it is more common to use third-party software to establish ssh connections. Widely used ssh clients are for instance MobaXterm, XShell, FinalShell, Terminus, PuTTY and Cygwin.

For using MobaXterm, you can either start a local terminal and use the same SSH command as for Linux and Mac OS X, or you can click on the session button, choose SSH and then enter the hostname and username. After clicking on OK, you will be asked to enter your password.

How to use MobaXterm: [How to access the cluster with MobaXterm - ETHZ](https://scicomp.ethz.ch/wiki/How_to_access_the_cluster_with_MobaXterm) / [Download and setup MobaXterm - CECI](https://support.ceci-hpc.be/doc/_contents/QuickStart/ConnectingToTheClusters/MobaXTerm.html)

How to use PuTTY: [How to access the cluster with PuTTY - ETHZ](https://scicomp.ethz.ch/wiki/How_to_access_the_cluster_with_PuTTY)

> An alternative option: use WSL/WSL2 [[CECI Doc]](https://support.ceci-hpc.be/doc/_contents/QuickStart/ConnectingToTheClusters/WSL.html)

### SSH keys

It is recommended to create SSH keys: Imagine when the network connection is unstable, typing the passwords, again and again, is frustrating. Using SSH Certificates, you will never need to type in the passwords during logging in. Powered by cryptography, it prevents man-in-the-middle attacks, etc.

The [links](#ssh-in-windows) above demonstrates methods using GUI. You can also create the keys with CLI:

### SSH keys on Linux

For security reasons, we recommend that you use a different key pair for every computer you want to connect to:

```bash
ssh-keygen -t ed25519 -f $HOME/.ssh/id_ed25519_cvgl_cluster
```

It is recommended to set a passphrase for the private key.

Once this is done, copy the public key to the cluster:

```bash
ssh-copy-id -i $HOME/.ssh/id_ed25519_cvgl_cluster.pub    username@login.cvgl.lab
```

Finally, you can add the private key to the ssh-agent temporarily so that you don't need to enter the passphrase every time (You still need to do this every time after reboot).

```bash
ssh-add ~/.ssh/id_ed25519_cvgl_cluster
```

### SSH keys on Windows
For Windows, a third-party software ([PuTTYgen](https://www.puttygen.com/), [MobaXterm](https://mobaxterm.mobatek.net/)) is commonly used to create SSH keys (demonstrated in the [links above](#ssh-in-windows)), however, since Windows 10, we can also follow similar steps in PowerShell:

- Step 1. On your PC, go to the folder:

```bat
mkdir ~/.ssh && cd ~/.ssh
```

- Step 2. Create a public/private key pair:

```bat
ssh-keygen -t ed25519 -f id_ed25519_cvgl_cluster
```

It's recommended to set a passphrase for the private key for advanced safety.

- Step 3. The program `ssh-copy-id` is not available so we manually copy the public key:

```bat
notepad ~/.ssh/id_ed25519_cvgl_cluster.pub
```

(Copy)

- Step 4. On the remote Server, create and edit the file, and paste the public key into it:

```bat
mkdir ~/.ssh && vim ~/.ssh/authorized_keys
```

(Paste to above and Save)

- Step 5. Start the ssh-agent; Apply the private key so that you don't need to enter the passphrase every time (You need to do this every time after the system starts up)

```bat
ssh-agent

ssh-add ~/.ssh/id_rsa
```

### Safety rules

- Always use a (strong) passphrase to protect your SSH key. Do not leave it empty!

- Never share your private key with somebody else, or copy it to another computer. It must only be stored on your personal computer

- Use a different key pair for each computer you want to connect to

- Do not reuse the key pairs for other systems

- Do not keep open SSH connections in detached `screen` sessions

- Disable the ForwardAgent option in your SSH configuration and do not use ssh -A (or use ssh -a to disable agent forwarding)

### How to use keys with non-default names

If you use different key pairs for different computers (as recommended above), you need to specify the right key when you connect, for instance:

```bash
ssh -p 22332 -i $HOME/.ssh/id_ed25519_cvgl_cluster username@login.cvgl.lab
```

To make your life easier, you can configure your ssh client to use these options automatically by adding the following lines in your $HOME/.ssh/config file:

```text
Host cluster
    HostName        login.cvgl.lab
    Port            22332
    User            username
    IdentityFile    ~/.ssh/id_ed25519_cvgl_cluster
```

For Windows, you need to use the backslash:

```text
IdentityFile    ~\\.ssh\\id_ed25519_cvgl_cluster
```

Then your ssh command simplifies as follows:

```bash
ssh cluster
```

## X11 forwarding and remote desktop

### X11 forwarding

Sometimes we need to run GUI applications on the login node. To directly run GUI applications in ssh terminals, you must open an SSH tunnel and redirect all X11 communication through that tunnel.

Xorg (X11) is normally installed by default as part of most Linux distributions. For Windows, tools such as [vcxsrv](https://sourceforge.net/projects/vcxsrv/) or [x410](https://x410.dev/) can be used. For macOS, since X11 is no longer included, you must install [XQuartz](https://www.xquartz.org/). You may want to check out the [Troubleshooting section](https://scicomp.ethz.ch/wiki/Accessing_the_clusters#Troubleshooting) by ETHZ IT-Services.

### Remote desktop via RDP

RDP (Remote Desktop Protocol) provides a remote desktop interface that is more user-friendly. To connect using RDP, you need an RDP Client installed. On Windows, there is a built-in remote desktop software `mstsc.exe`, or you can download a newer `Microsoft Remote Desktop` from the Microsoft Store.

On Linux, it's recommended to install `Remmina` and `remmina-plugin-rdp`.

Using the RDP Clients is simple. Following the prompts, type in the server address, user name and password. Then, set the screen resolution and color depth you want.

For security, RDP is only allowed from SSH tunnels, and the default RDP port is also changed from 3389 to 23389. One can create the SSH tunnel and forward RDP connections to localhost:23389 by

```bash
ssh -p 22332 -NL 23389:localhost:23389 username@login.cvgl.lab
```

Then connect to `localhost:23389` using `mstsc.exe` or Remote Desktop App from [Microsoft Store](https://apps.microsoft.com/store/detail/microsoft-remote-desktop/9WZDNCRFJ3PS)

<details>
<summary> Click to show image</summary>

![mstsc1](Getting_started/QQ%E6%88%AA%E5%9B%BE20220316211436.png)
![mstsc2](Getting_started/QQ截图20220316211450.png)

</details>

# Data management

## Introduction

![Storage Model](Getting_started/storage_model.svg)

We are currently using NFS to share filesystems between cluster nodes. The storage space of the login node is small (about 100GB), so it is recommended to store code and data in NFS shared folders: `/dataset` for datasets and `/workspace` for workspaces. The two NFS folders are allocated on the storage server, which currently offers a capacity of 143TB, with data redundancy and snapshot capability powered by TrueNAS ZFS.

You need to ask the system admin to create your workspace folder `/workspace/<username>`.

By default, other users do not have either read or write [permissions](https://scicomp.ethz.ch/wiki/Linux_permissions) on your folder.

## Uploading and downloading data

### Uploading

When you transfer data from your personal computer to a storage server, it's called an upload.
We can use CLI tools like `scp`, `rsync`; or GUI tools like `mobaXterm`, `FinalShell`, `VSCode`, `xftp`, `SSHFS` for uploading files from a personal computer to the data storage.

Here is an example of using `FinalShell`:

<details>
<summary> Click to show image</summary>

![FinalShell](Getting_started/QQ截图20220624200336.png)
</details>

Here is an example of using SSHFS-win:

<details>
<summary> Click to show image</summary>

![FinalShell](Getting_started/QQ截图20220624203058.png)
</details>

### Downloading

When you get data from a service provider such as Baidu Netdisk, Google Drive, Microsoft Onedrive, Amazon S3, etc., it's called a download. For example, you can use the Baidu Netdisk client (already installed).
You can also download datasets directly from the source. It is recommended to use professional download software to download large datasets, such as aria2, motrix (aria2 with GUI), etc.

Here is an example of using Baidu Netdisk:

<details>
<summary> Click to show image</summary>

![baidu_netdisk](Getting_started/QQ截图20220317001515.png)
</details>

### Using proxy service

#### Self-provisioned services

We have configured both HTTP and SOCKS5 proxy services on the cluster:

##### RackNerd US: Los Angeles DC-03 Datacenter, with 12TB/mo **lots of** traffic
  - Service: 5 GB KVM VPS (Black Friday 2024)
  - Annually: $55.93
  - Routing: Basic BGP
  - http://10.0.1.68:58889
  - socks5://10.0.1.68:50089

##### Oracle Cloud Japan: Osaka, with 10TB/mo **free** traffic (14 USD/TB beyond)
  - http://10.0.1.68:48889
  - socks5://10.0.1.68:40089

##### Bandwagon US: Los Angeles DC1, with 2TB/mo traffic
  - Service: NODESEEK-MEGABOX-PRO
  - Annually: $45.68
  - Routing: (DC1 CT CN2GIA, CMIN2) [USCA_1]
  - http://10.0.1.68:28889
  - socks5://10.0.1.68:20089

##### Bandwagon US: Los Angeles DC6, with 1TB/mo **fast** traffic
  - Service: SPECIAL 40G KVM PROMO V5 - LOS ANGELES - CN2 GIA LIMITED EDITION
  - Annually: $93.10
  - Routing: (DC6 CT CN2GIA-E, CMIN2, CUP) [USCA_6]
  - http://10.0.1.68:18889
  - socks5://10.0.1.68:10089

#### IPLC services

We have purchased IPLC services from Bandwagon Host:
- Service: JMS IPLC HK 1000 V2 EARLY ACCESS
- Annually: $558.37
- Routing: HongKong IPLC

> You can ask for out-of-campus access from the system admin.

Deployed proxies services:

##### IPLC-HK01
Campus Network
```
socks5://10.0.1.68:50180
http://10.0.1.68:50189
```
Cluster 100G LAN
```
socks5://192.168.233.8:50180
http://192.168.233.8:50180
```

##### IPLC-HK02
Campus Network
```
socks5://10.0.1.68:50280
http://10.0.1.68:50289
```
Cluster 100G LAN
```
socks5://192.168.233.8:50289
http://192.168.233.8:50289
```

##### IPLC-US52
Campus Network
```
socks5://10.0.1.68:55280
http://10.0.1.68:55289
```
Cluster 100G LAN
```
socks5://192.168.233.8:55280
http://192.168.233.8:55280
```

##### IPLC-US53
Campus Network
```
socks5://10.0.1.68:55380
http://10.0.1.68:55389
```
Cluster 100G LAN
```
socks5://192.168.233.8:55380
http://192.168.233.8:55380
```

##### jms-iplc-temp-workaround-hk-s01
Campus Network
```
socks5://10.0.1.68:59180
http://10.0.1.68:59189
```
Cluster 100G LAN
```
socks5://192.168.233.8:59180
http://192.168.233.8:59189
```

##### jms-iplc-temp-workaround-us-s02
Campus Network
```
socks5://10.0.1.68:59280
http://10.0.1.68:59289
```
Cluster 100G LAN
```
socks5://192.168.233.8:59280
http://192.168.233.8:59289
```


#### Proxychains

Project homepage: [proxychains-ng](https://github.com/rofl0r/proxychains-ng)

Example Usage:

```bash
proxychains curl google.com

proxychains -q curl google.com # Quite mode

proxychains git clone https://github.com/WU-CVGL/BAD-NeRF
```

#### Any python downloading that uses `urllib`

Add this code snippet right after the `import urllib`:

```python
import urllib

print("configuring proxy...")

proxy_support = urllib.request.ProxyHandler({
    'http' : 'http://10.0.1.68:28889', 
    'https': 'http://10.0.1.68:28889'
})
opener = urllib.request.build_opener(proxy_support)
urllib.request.install_opener(opener)
```

> Ref: https://docs.python.org/3/library/urllib.request.html#urllib.request.build_opener

#### Huggingface

Just use the `hf-mirror` service.

```sh
export HF_ENDPOINT=https://hf-mirror.com
```

or in python script:

```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
```

> Ref: https://hf-mirror.com/

#### Environment variable

Export these environment variables before program execution.

This is useful when some programs that do not use `libc` cannot be hooked by `proxychains`,
such as many programs written in `python` or `golang`.

```bash
export http_proxy=http://10.0.1.68:28889 &&\
export https_proxy=http://10.0.1.68:28889 &&\
export HTTP_PROXY=http://10.0.1.68:28889 &&\
export HTTPS_PROXY=http://10.0.1.68:28889
curl google.com
```

Outputs:

```text
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>
```

If this proxy server does not work well, you can try another proxy service:

```bash
export http_proxy=http://10.0.1.68:28889 &&\
export https_proxy=http://10.0.1.68:28889 &&\
export HTTP_PROXY=http://10.0.1.68:28889 &&\
export HTTPS_PROXY=http://10.0.1.68:28889
curl google.com
```

> P.S. You can monitor the status of the proxy services in the [grafana dashboard](https://grafana.cvgl.lab/d/CCSvIIEZz/v2ray-dashboard?orgId=1).


### Using our aria2 service

You can use our deployed aria2 server on the login-node to download large datasets on the serverside.

It is deployed on this URL:

```text
http://10.0.1.67:6800/jsonrpc
```

And you need to ask the administrator for the password.

1. First install the AriaNg browser extension. You can install it from the [Chrome web store](https://chromewebstore.google.com/detail/aria2-explorer/mpkodccbngfoacfalldjimigbofkhgjn).
2. Pin the extension. ![pin-browser-extension](./Getting_started/pin_aria_ng.png)
3. Configure the web UI. ![aria-ng-config](./Getting_started/aria_ng_config.png)
4. Configure the extension options for monitoring and automatic download capture. ![aria-ng-options](./Getting_started/aria_ng_options.png)
5. You can also manually create download tasks. First configure the download options, set `max-conn-per-server` (`5` in the image below) to larger values like `16`. Also change the `all-proxy` (`6` in the image below)if needed. If the server of the desired resource is located in the mainland China, then you can make this value empty. Finally paste the download URLs in the first tab (`7` in the image below). ![manual-tasks](./Getting_started/aria_ng_manual.png)

