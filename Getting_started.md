<h1 align="center">Getting started with the cluster</h1>
<p align="center">2022-03-15 v0.2</p>

# Requesting accounts

The accounts includes a Linux account on the login node, and an account for the batch system (Determined AI).

# Accessing the cluster

## Security
Accessing to the cluster is currently only possible via secure protocols (ssh, scp, rsync). The cluster is only accessible from inside the campus local area network. If you would like to connect from a computer, which is not inside the campus network, then you would need to establish a [VPN](https://vpn.westlake.edu.cn/) connection first.

## Hosts
Since our cluster is only accesible in the campus LAN, and we do not have the administration of the DNS server, setting up the *hosts* file is the best way to translate human-friendly hostnames into IP addresses.

The way to modify the hosts file is as follows:

### For Windows

- Press `Win-Key + R`. A a small window will pop up.

- Type in the following command and press `Ctrl+Shift+Enter`, to make notepad run as administrator and edit the *hosts* file.

    notepad C:\Windows\System32\drivers\etc\hosts

### For Linux, *nix including macOS

- Edit `/etc/hosts` with root privilege in your favourite way. For example:

    sudo vim /etc/hosts

### Hosts Modification

Append these lines to the end of the *hosts* file:

    10.0.1.67 cvgl.lab
    10.0.1.67 git.cvgl.lab
    10.0.1.67 gpu.cvgl.lab
    10.0.1.68 login.cvgl.lab

## Install the root CA certificate (Optional)

Since we are using a self-signed certificate, after modifying the host, when we use a web browser to access the service, a security warning appears saying the certificate is not recognized. We can suppress this warning by making the system trust the certificate.

The certificate can be downloaded at: [https://cvgl.lab/cvgl.crt](https://cvgl.lab/cvgl.crt)

- For Windows, right click the CA certificate file and select 'Install Certificate'. Follow the prompts to add the certificate to the **Trusted Root Certification Authorities**.
- For Linux (tested Ubuntu), first you need the `ca-certificates` package installed, then copy the certificate file to `/usr/local/share/ca-certificates`, and update certificates system-wide with the following command:

    sudo update-ca-certificates

## SSH
You can connect to the cluster via the SSH protocol. For this purpose it is required that you have an SSH client installed. The information required to connect to the cluster, is the hostname (which resolves to an IP address) of the cluster and your account credentials (username, password).

Since we have set up the *hosts* in the [previous section](#hosts), we can use the human-readable hostname to make our connection.

| Hostname | IP Address |
| :-- | :-- |
|login.cvgl.lab|10.0.1.68|

### SSH in Linux, *nix including macOS
Open a terminal and use the standard ssh command

    ssh -p 22332 username@hostname

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

<details>
<summary> Click to show </summary>

### SSH keys on Linux
For security reasons, we recommend that you use a different key pair for every computer you want to connect to:

    ssh-keygen -t ed25519 -f $HOME/.ssh/id_ed25519_cvgl_cluster
    
    (And hit ENTER multiple times)

    (You can set a passphrase for the private key for advanced safety)

Once this is done, copy the public key to the cluster:

    ssh-copy-id -i $HOME/.ssh/id_ed25519_cvgl_cluster.pub    username@login.cvgl.lab

Finally you can add the private key temporarily so that you don't need to enter passphrase every time (You still need to do this every time after reboot)

    ssh-add ~/.ssh/id_ed25519_cvgl_cluster

### SSH keys on Windows
For windows a third party software ([PuTTYgen](https://www.puttygen.com/),[MobaXterm](https://mobaxterm.mobatek.net/)) is commonly used to create SSH keys (demonstrated in the [links above](#ssh-in-windows)).
However since Windows 10, we can also follow the similar steps in powershell:
- Step 1. On your PC, go to folder:

    mkdir ~/.ssh && cd ~/.ssh

- Step 2. Create a public/private key pair:

    ssh-keygen

    (Set a passphrase for the private key for advanced safety)

- Step 3. The program `ssh-copy-id` is not available so we manually copy the public key:

    cat ~/.ssh/id_rsa.pub

    (Copy)

- Step 4. On remote Server, create and edit file, paste the public key into it:

    mkdir ~/.ssh && vim ~/.ssh/authorized_hosts

    (Paste and Save)

- Step 5. Start the ssh-agent; Apply the private key so that you don't need to enter passphrase every time (You need to do this every time after system starts up)

    ssh-agent

    ssh-add ~/.ssh/id_rsa

</details>

### Safety rules

- Always use a (strong) passphrase to protect your SSH key. Do not leave it empty!

- Never share your private key with somebody else, or copy it to another computer. It must only be stored on your personal computer

- Use a different key pair for each computer you want to connect to

- Do not reuse the key pairs for Euler / Leonhard for other systems

- Do not keep open SSH connections in detached screen sessions

- Disable the ForwardAgent option in your SSH configuration and do not use ssh -A (or use ssh -a to disable agent forwarding)

### How to use keys with non-default names

If you use different key pairs for different computers (as recommended above), you need to specify the right key when you connect, for instance:

    ssh -p 22332 -i $HOME/.ssh/id_ed25519_cvgl_cluster username@login.cvgl.lab

To make your life easier, you can configure your ssh client to use these options automatically by adding the following lines in your $HOME/.ssh/config file:

    Host cluster
        HostName        login.cvgl.lab
        Port            22332
        User            username
        IdentityFile    ~/.ssh/id_ed25519_cvgl_cluster

Then your ssh command simplifies as follows:

    ssh cluster

## X11 forwarding and remote desktop

Sometimes we need to run GUI applications on the login node. To directly run GUI application in ssh terminal, you must open an SSH tunnel and redirect all X11 communication through that tunnel.

### X11 over SSH on Linux, *nix including macOS

Xorg (X11) is normally installed by default as part of most Linux distributions. For macOS, since X11 is no longer included, you must install [XQuartz](https://www.xquartz.org/). You may need to check out the [trubleshooting section](https://scicomp.ethz.ch/wiki/Accessing_the_clusters#Troubleshooting) authored by ETH.


### Remote desktop via RDP

RDP (Remote Desktop Protocol) provides a remote desktop interface which is more user-friendly. To connect using RDP, you need an RDP Client installed. On Windows, there is a built-in remote deskto software `mstsc.exe`, or you can download a newer `Microsoft Remote Desktop` from the Microsoft Store.
On Linux, it's recommended to install Remmina and remmina-plugin-rdp.

Using the RDP Clients is simple. Following the prompts, type in the server address, user name, password, set the screen resolution and color depth you want.

![remmina](Getting_started/QQ截图20220310230912.png)
![mstsc](Getting_started/QQ截图20220310231310.png)

# Data management

(TODO: home/storage on login node, NFS, GlusterFS, dataset, netdisk)