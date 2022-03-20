<h1 align="center">Getting started with the cluster</h1>
<p align="center">2022-03-17 v0.2a</p>

- [Requesting accounts](#requesting-accounts)
- [Accessing the cluster](#accessing-the-cluster)
  - [Security](#security)
  - [Setting up the hosts file](#setting-up-the-hosts-file)
    - [For Windows](#for-windows)
    - [For Linux, *nix including macOS](#for-linux-nix-including-macos)
    - [Hosts Modification](#hosts-modification)
  - [Install the root CA certificate (Optional)](#install-the-root-ca-certificate-optional)
  - [SSH](#ssh)
    - [SSH in Linux, *nix including macOS](#ssh-in-linux-nix-including-macos)
    - [SSH in Windows](#ssh-in-windows)
    - [SSH keys](#ssh-keys)
    - [SSH keys on Linux](#ssh-keys-on-linux)
    - [SSH keys on Windows](#ssh-keys-on-windows)
    - [Safety rules](#safety-rules)
    - [How to use keys with non-default names](#how-to-use-keys-with-non-default-names)
  - [X11 forwarding and remote desktop](#x11-forwarding-and-remote-desktop)
    - [Remote desktop via RDP](#remote-desktop-via-rdp)
- [Data management](#data-management)
  - [Introduction](#introduction)
  - [Uploading and downloading data](#uploading-and-downloading-data)

# Requesting accounts

Accounts that need to be created by the administrator include:
- A Linux account on the login node ([login.cvgl.lab](https://login.cvgl.lab/))
- An account for the batch system (Determined AI, [gpu.cvgl.lab](https://gpu.cvgl.lab/)).
- A Nextcloud account ([pan.cvgl.lab](https://pan.cvgl.lab/))

Accounts that you can create by your self:
- Gitea account ([git.cvgl.lab](https://git.cvgl.lab/))

# Accessing the cluster

## Security
Accessing to the cluster is currently only possible via secure protocols (ssh, scp, rsync). The cluster is only accessible from inside the campus local area network. If you would like to connect from a computer, which is not inside the campus network, then you would need to establish a [VPN](https://vpn.westlake.edu.cn/) connection first.

## Setting up the hosts file
Since our cluster is only accesible in the campus LAN, and we do not have the administration of the DNS server, setting up the *hosts* file is the best way to translate human-friendly hostnames into IP addresses.

The way to modify the hosts file is as follows:

### For Windows

- Press `Win-Key + R`. A a small window will pop up.

- Type in the following command and press `Ctrl+Shift+Enter`, to make notepad run as administrator and edit the *hosts* file.
```
notepad C:\Windows\System32\drivers\etc\hosts
```
### For Linux, *nix including macOS

- Edit `/etc/hosts` with root privilege in your favourite way. For example:
```
sudo vim /etc/hosts
```
### Hosts Modification

Append these lines to the end of the *hosts* file:
```
10.0.1.67 cvgl.lab
10.0.1.67 git.cvgl.lab
10.0.1.67 gpu.cvgl.lab
10.0.1.67 pan.cvgl.lab
10.0.1.68 login.cvgl.lab
```
## Install the root CA certificate (Optional)

Since we are using a self-signed certificate, after modifying the host, when we use a web browser to access the service, a security warning appears saying the certificate is not recognized. We can suppress this warning by making the system trust the certificate.

The certificate can be downloaded at: [https://cvgl.lab/cvgl.crt](https://cvgl.lab/cvgl.crt)

- For Windows, right click the CA certificate file and select 'Install Certificate'. Follow the prompts to add the certificate to the **Trusted Root Certification Authorities**. If you are using Git for Windows, you will need to configure Git to use Windows native crypto backend: `git config --global http.sslbackend schannel`

- For Linux (tested Ubuntu), first you need the `ca-certificates` package installed, then copy the `.crt` file into the folder `/usr/local/share/ca-certificates`, and update certificates system-wide with the command `sudo update-ca-certificates`. This works for most applications, but browsers like google-chrome and chromium on Linux has its own certificate storage. You need to go to `chrome://settings/certificates`, select "Authorities", and import the `.crt` file. To use our Docker registry `registry.cvgl.lab`, you need to create the folder `/etc/docker/certs.d/registry.cvgl.lab/` and copy ther certificate into it.


## SSH
You can connect to the cluster via the SSH protocol. For this purpose it is required that you have an SSH client installed. The information required to connect to the cluster, is the hostname (which resolves to an IP address) of the cluster and your account credentials (username, password).

Since we have set up the *hosts* in the [previous section](#hosts), we can use the human-readable hostname to make our connection.

| Hostname | IP Address |
| :-- | :-- |
|login.cvgl.lab|10.0.1.68|

### SSH in Linux, *nix including macOS
Open a terminal and use the standard ssh command
```
ssh -p 22332 username@hostname
```
where **username** is your username and the **hostname** can be found in the table shown above. The parameter `-p 22332` is used to declare the SSH port used on the server. For security, we modified the default port. If for instance user **peter** would like to access the cluster, then the command would be

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
    Swap usage:   0%                  IPv4 address for enp6s0:  10.0.1.68
    Processes:    278

    0 updates can be applied immediately.

    Last login: Tue Mar 15 11:29:19 2022 from 172.16.29.72

Note that when it prompts to enter the password:

    peter@login.cvgl.lab's password:

there will not be any visual feedback (i.e. asterisks) in order not to show the length of your password.

### SSH in Windows
Since Windows 10, an ssh client is also provided in the operating system, but it is more common to use a third-party software to establish ssh connections. Widely used ssh clients are for instance MobaXterm, XShell, FinalShell, Terminus, PuTTY and Cygwin.

For using MobaXterm, you can either start a local terminal and use the same SSH command as for Linux and Mac OS X, or you can click on the session button, choose SSH and then enter the hostname and username. After clicking on OK, you will be asked to enter your password.

Here is an example about how to use MobaXterm: [How to access the cluster with MobaXterm](https://scicomp.ethz.ch/wiki/How_to_access_the_cluster_with_MobaXterm)

Here is an example about how to use PuTTY: [How to access the cluster with PuTTY](https://scicomp.ethz.ch/wiki/How_to_access_the_cluster_with_PuTTY)


### SSH keys
It is recommended to create SSH keys: Imagine when the network connection is unstable, typing the passwords again and agiain is frustrating. Using SSH Certificates, you will never need to type in the passwords, while it provides more safety, powered by cryptography, it prevents man-in-the-middle attacks, etc.

The [links](#ssh-in-windows) above demonstrates methods using GUI. You can also create the keys with CLI:


### SSH keys on Linux
For security reasons, we recommend that you use a different key pair for every computer you want to connect to:
```
ssh-keygen -t ed25519 -f $HOME/.ssh/id_ed25519_cvgl_cluster
```   
It is recommended to set a passphrase for the private key.

Once this is done, copy the public key to the cluster:
```
ssh-copy-id -i $HOME/.ssh/id_ed25519_cvgl_cluster.pub    username@login.cvgl.lab
```
Finally you can add the private key to the ssh-agent temporarily so that you don't need to enter passphrase every time (You still need to do this every time after reboot).
```
ssh-add ~/.ssh/id_ed25519_cvgl_cluster
```

### SSH keys on Windows
For windows a third party software ([PuTTYgen](https://www.puttygen.com/), [MobaXterm](https://mobaxterm.mobatek.net/)) is commonly used to create SSH keys (demonstrated in the [links above](#ssh-in-windows)).
However since Windows 10, we can also follow the similar steps in powershell:
- Step 1. On your PC, go to folder:
```
mkdir ~/.ssh && cd ~/.ssh
```
- Step 2. Create a public/private key pair:
```
ssh-keygen -t ed25519
```
It's recommended to set a passphrase for the private key for advanced safety.

- Step 3. The program `ssh-copy-id` is not available so we manually copy the public key:
```
cat ~/.ssh/id_ed25519.pub
```
(Copy above)

- Step 4. On remote Server, create and edit file, paste the public key into it:
```
mkdir ~/.ssh && vim ~/.ssh/authorized_hosts
```
(Paste to above and Save)

- Step 5. Start the ssh-agent; Apply the private key so that you don't need to enter passphrase every time (You need to do this every time after system starts up)
```
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
```
ssh -p 22332 -i $HOME/.ssh/id_ed25519_cvgl_cluster username@login.cvgl.lab
```
To make your life easier, you can configure your ssh client to use these options automatically by adding the following lines in your $HOME/.ssh/config file:
```
Host cluster
    HostName        login.cvgl.lab
    Port            22332
    User            username
    IdentityFile    ~/.ssh/id_ed25519_cvgl_cluster
```
Then your ssh command simplifies as follows:
```
ssh cluster
```
## X11 forwarding and remote desktop

Sometimes we need to run GUI applications on the login node. To directly run GUI application in ssh terminal, you must open an SSH tunnel and redirect all X11 communication through that tunnel.

Xorg (X11) is normally installed by default as part of most Linux distributions. For Windows, tools such as [vcxsrv](https://sourceforge.net/projects/vcxsrv/) or [x410](https://x410.dev/) can be used. For macOS, since X11 is no longer included, you must install [XQuartz](https://www.xquartz.org/). You may want to check out the [Troubleshooting section](https://scicomp.ethz.ch/wiki/Accessing_the_clusters#Troubleshooting) by ETHZ IT-Services.


### Remote desktop via RDP

RDP (Remote Desktop Protocol) provides a remote desktop interface which is more user-friendly. To connect using RDP, you need an RDP Client installed. On Windows, there is a built-in remote deskto software `mstsc.exe`, or you can download a newer `Microsoft Remote Desktop` from the Microsoft Store.
On Linux, it's recommended to install Remmina and remmina-plugin-rdp.

Using the RDP Clients is simple. Following the prompts, type in the server address, user name, password, set the screen resolution and color depth you want.

For security, we changed the default RDP port from 3389 to 23389. So the server address becomes:
```
login.cvgl.lab:23389
```
<details>
<summary> Click to show image</summary>

![mstsc1](Getting_started/QQ%E6%88%AA%E5%9B%BE20220316211436.png)
![mstsc2](Getting_started/QQ截图20220316211450.png)

</details>

# Data management

## Introduction

We are currently using NFS to share filesystems between cluster nodes. The storage space of the login node is small (about 100GB), so it is recommended to store code and data in NFS shared folders: `/dataset` for datasets and `/workspace` for workspaces. The two NFS folders are allocated on two different SSDs, each with a capacity of 2TB.

We can check the file systems with command `df -H`:

    peter@login.cvgl.lab: ~ $ df -H

    Filesystem                Size  Used Avail Use% Mounted on
    /dev/vda2                 135G   40G   89G  31% /
    192.168.122.1:/datasets   2.0T  217G  1.7T  12% /datasets
    192.168.122.1:/workspace  2.0T  217G  1.7T  12% /workspace

We can create your own folder under workspace:

    mkdir /workspace/<username>

By default, other users have read [permissions](https://scicomp.ethz.ch/wiki/Linux_permissions) on your folder. We can also make it private:

    chmod 700 /workspace/<username>

## Uploading and downloading data

We can use CLI tools like scp, rsync; or GUI tools like mobaXterm, VSCode, xftp for uploading files from a personal computer to the data storage. Or you can use Baidu Netdisk client (already installed). You can also download datasets directly from the source. It is recommended to use professional download software to download large datasets, such as aria2, motrix (aria2 with GUI), etc.

<details>
<summary> Click to show image</summary>

![baidu_netdisk](Getting_started/QQ截图20220317001515.png)
</details>

