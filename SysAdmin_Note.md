<h1 align="center">SysAdmin's Note</h1>
<p align="center">2022-03-15 v0.2</p>

- [Topology](#topology)
- [Networking](#networking)
- [UFW](#ufw)
- [NFS](#nfs)
- [XRDP](#xrdp)
- [I18N](#i18n)
- [Nginx Reverse Proxy & HTTPS/TLS](#nginx-reverse-proxy--httpstls)

# Topology

The cluster currently has one physical server, with Ubuntu 20.04 & QEMU-KVM installed. Two VMs are created on the host: a login node & a Determined AI Master node. The host is also a Determined AI Agent node. Nginx, Gitea, and other Web-based services are deployed by Docker on the host.

# Networking

IP address range: 10.0.1.64/27

Gateway: 10.0.1.65

IP address pool: 10.0.1.66-94

BMC(IPMI) of Node01 has be assigned the IP Address 10.0.1.66.

    # cvgl-node01
    vim /etc/netplan/00-installer-config.yaml
    ####
    network:
        ethernets:
            eno2:
            dhcp4: false
            addresses: [10.0.1.67/27]
            gateway4: 10.0.1.65
            nameservers:
                addresses: [10.10.10.10]
        version: 2


Two VMs are connected to the host by NAT-bridge, and connected to the campus network by macvtap-bridge.

    # cvgl-node01-vm01
    vim /etc/netplan/00-installer-config.yaml
    ####
    network:
        ethernets:
            enp1s0:
            addresses:
            - 192.168.122.2/24
            routes:
            - to: 192.168.122.0/24
                via: 192.168.122.1
                on-link: true
        #      gateway4: 192.168.122.1
            nameservers:
                addresses:
                - 10.10.10.10
                - 223.6.6.6
            enp6s0:
            addresses:
            - 10.0.1.68/27
            routes:
            - to: 0.0.0.0/0
                via: 10.0.1.65
                on-link: true
        #     gateway4: 10.0.1.65
            nameservers:
                addresses:
                - 10.10.10.10
                - 223.6.6.6
                search: []
        version: 2
    ####


    # cvgl-node01-vm02
    vim /etc/netplan/00-installer-config.yaml
    ####
    network:
        ethernets:
            enp1s0:
            addresses:
            - 192.168.122.3/24
            routes:
            - to: 192.168.122.0/24
                via: 192.168.122.1
                on-link: true
        #      gateway4: 192.168.122.1
            nameservers:
                addresses:
                - 10.10.10.10
                - 223.6.6.6
            enp6s0:
            addresses:
            - 10.0.1.69/27
            routes:
            - to: 0.0.0.0/0
                via: 10.0.1.65
                on-link: true
        #     gateway4: 10.0.1.65
            nameservers:
                addresses:
                - 10.10.10.10
                - 223.6.6.6
                search: []
        version: 2
    ####

# UFW

    # On Node01
    To                         Action      From
    --                         ------      ----
    222                        ALLOW       Anywhere       # Gitea SSH
    443                        ALLOW       Anywhere       # nginx
    2049                       ALLOW       10.0.1.64/27   # NFS
    3000                       ALLOW       Anywhere       # Gitea HTTP
    8080                       ALLOW       10.0.1.64/27   # Determined intra-cluster (inter-node)
    22332                      ALLOW       Anywhere       # SSH
    23389                      ALLOW       Anywhere       # RDP


# NFS
    # On Node01 as NFS server
    apt install nfs-kernel-server
    mkdir -p /srv/nfs4/datasets
    mkdir -p /srv/nfs4/worspace
    echo "/datasets /srv/nfs4/backups none bind 0 0" >> /etc/fstab
    echo "/mnt/sdb1/workspace /srv/nfs4/workspace none bind 0 0" >> /etc/fstab
    mount -a
    mkdir /workspace
    sudo mount --bind /mnt/sdb1/workspace /workspace
    vim /etc/exports
    ####
    /srv/nfs4            10.0.1.64/27(rw,sync,no_subtree_check,crossmnt,fsid=0)
    /srv/nfs4            192.168.122.0/24(rw,sync,no_subtree_check,crossmnt,fsid=0)
    /srv/nfs4/datasets   10.0.1.64/27(rw,sync,no_subtree_check)
    /srv/nfs4/datasets   192.168.122.0/24(rw,sync,no_subtree_check)
    /srv/nfs4/workspace  10.0.1.64/27(rw,sync,no_subtree_check)
    /srv/nfs4/workspace  192.168.122.0/24(rw,sync,no_subtree_check)
    ####
    exportfs -ar
    
    # On Node01VM01 as NFS client
    apt install nfs-common
    mkdir -p /datasets
    mkdir -p /workspace
    echo "192.168.122.1:/datasets /datasets nfs defaults,timeo=900,retrans=5,_netdev 0 2" >> /etc/fstab
    echo "192.168.122.1:/workspace /workspace nfs defaults,timeo=900,retrans=5,_netdev 0 2" >> /etc/fstab
    mount -a

# XRDP
> https://www.reddit.com/r/linuxquestions/comments/ceog3w/how_can_i_install_xrdp_so_that_it_actually_works/

# I18N
````
sudo apt-get -y install `check-language-support -l zh-hans`
````

# Nginx Reverse Proxy & HTTPS/TLS

    docker pull nginx

    docker run -d --name nginx nginx

    mkdir -p /mnt/sda1/docker/nginx/data
    mkdir -p /mnt/sda1/docker/nginx/config
    mkdir -p /mnt/sda1/docker/nginx/logs

    docker cp nginx:/usr/share/nginx/html /mnt/sda1/docker/nginx/data/
    docker cp nginx:/etc/nginx /mnt/sda1/docker/nginx/config/
    docker cp nginx:/var/log/nginx /mnt/sda1/docker/nginx/logs/

    docker rm -f nginx

    mkdir -p /mnt/sda1/docker/nginx/ssl


    # Creating Self-Signed Certificates and Keys with OpenSSL
    # Better Set Passphrase for Keys
    cd /mnt/sda1/docker/nginx/ssl

    vim CA.cnf
    ####
    [req]
    distinguished_name  = req_distinguished_name
    x509_extensions     = root_ca
    prompt              = no

    [req_distinguished_name]
    C   = CN
    ST  = Zhejiang
    L   = Hangzhou
    O   = Westlake University
    OU  = SOE
    CN  = cvgl.lab

    [root_ca]
    basicConstraints    = critical, CA:true
    ####

    vim Server.ext
    ####
    extendedKeyUsage = serverAuth
    subjectAltName = @alt_names

    [alt_names]
    DNS.1 = cvgl.lab
    DNS.2 = *.cvgl.lab
    ####

    # Create CA Certificate
    openssl req -x509 -newkey rsa:2048 -out CA.cer -outform PEM -keyout CA.pvk -days 10000 -verbose -config CA.cnf -subj "/CN=CVGL SOE Westlake University CA"

    # Create Server Certificate
    openssl req -newkey rsa:2048 -keyout Server.pvk -out Server.req -subj /CN=cvgl.lab
    openssl x509 -req -CA CA.cer -CAkey CA.pvk -in Server.req -out Server.cer -days 10000 -extfile Server.ext -set_serial 0x1111
    
    # If keys have passphrase
    openssl rsa -in Server.pvk -out Server-unsecure.pvk


    vim  /mnt/sda1/docker/nginx/config/nginx/conf.d/default.conf
    ####
    # top-level http config for websocket headers
    # If Upgrade is defined, Connection = upgrade
    # If Upgrade is empty, Connection = close
    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }

    server {
        listen 80;
        server_name NO_HUB.DOMAIN.TLD;

        # Tell all requests to port 80 to be 302 redirected to HTTPS
        return 302 https://$host$request_uri;
    }

    server {
        listen       443 ssl;
        server_name  cvgl.lab;

        #access_log  /var/log/nginx/host.access.log  main;

        ssl on;
        ssl_certificate /opt/ssl/Server.cer;
        ssl_certificate_key /opt/ssl/Server-unsecure.pvk;
        ssl_session_timeout 5m;
        ssl_protocols TLSv1.2 TLSv1.3;

        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
        }

        #error_page  404              /404.html;

        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   /usr/share/nginx/html;
        }
    }

    server {
        listen       443 ssl;
        server_name  git.cvgl.lab;

        #access_log  /var/log/nginx/host.access.log  main;

        ssl on;
        ssl_certificate /opt/ssl/Server.cer;
        ssl_certificate_key /opt/ssl/Server-unsecure.pvk;
        ssl_session_timeout 5m;
        ssl_protocols TLSv1.2 TLSv1.3;

        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        location / {
            proxy_pass http://localhost:3000;
        }

        #error_page  404              /404.html;

        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   /usr/share/nginx/html;
        }
    }

    server {
        listen       443 ssl;
        server_name  gpu.cvgl.lab;

        #access_log  /var/log/nginx/host.access.log  main;

        ssl on;
        ssl_certificate /opt/ssl/Server.cer;
        ssl_certificate_key /opt/ssl/Server-unsecure.pvk;
        ssl_session_timeout 5m;
        ssl_protocols TLSv1.2 TLSv1.3;

        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # disable any limits to avoid HTTP 413 for large image uploads
        client_max_body_size 0;

        # required to avoid HTTP 411: see Issue #1486 (https://github.com/moby/moby/issues/1486)
        chunked_transfer_encoding on;

        location / {
            proxy_pass http://192.168.122.3:8080;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            # websocket headers
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header X-Scheme $scheme;

            proxy_buffering off;
        }

        #error_page  404              /404.html;

        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   /usr/share/nginx/html;
        }
    }

    upstream docker-registry {
        server localhost:5000;
    }

    ## Set a variable to help us decide if we need to add the
    ## 'Docker-Distribution-Api-Version' header.
    ## The registry always sets this header.
    ## In the case of nginx performing auth, the header is unset
    ## since nginx is auth-ing before proxying.
    map $upstream_http_docker_distribution_api_version $docker_distribution_api_version {
        '' 'registry/2.0';
    }

    server {
        listen       443 ssl;
        server_name  registry.cvgl.lab;

        #access_log  /var/log/nginx/host.access.log  main;

        ssl on;
        ssl_certificate /opt/ssl/Server.cer;
        ssl_certificate_key /opt/ssl/Server-unsecure.pvk;

        # Recommendations from https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers 'EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH';
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;

        # disable any limits to avoid HTTP 413 for large image uploads
        client_max_body_size 0;

        # required to avoid HTTP 411: see Issue #1486 (https://github.com/moby/moby/issues/1486)
        chunked_transfer_encoding on;


        location /v2/ {
            # Do not allow connections from docker 1.5 and earlier
            # docker pre-1.6.0 did not properly set the user agent on ping, catch "Go *" user agents
            if ($http_user_agent ~ "^(docker\/1\.(3|4|5(?!\.[0-9]-dev))|Go ).*$" ) {
                return 404;
            }
            # To add basic authentication to v2 use auth_basic setting.
            auth_basic "Registry realm";
            auth_basic_user_file /etc/nginx/conf.d/nginx.htpasswd;
            ## If $docker_distribution_api_version is empty, the header is not added.
            ## See the map directive above where this variable is defined.
            add_header 'Docker-Distribution-Api-Version' $docker_distribution_api_version always;

            proxy_pass                          http://docker-registry;
            proxy_set_header  Host              $http_host;   # required for docker client's sake
            proxy_set_header  X-Real-IP         $remote_addr; # pass on real client's IP
            proxy_set_header  X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header  X-Forwarded-Proto $scheme;
            proxy_read_timeout                  900;
        }
    }


    server {
        listen       443 ssl;
        server_name  portainer.cvgl.lab;

        #access_log  /var/log/nginx/host.access.log  main;

        ssl on;
        ssl_certificate /opt/ssl/Server.cer;
        ssl_certificate_key /opt/ssl/Server-unsecure.pvk;
        ssl_session_timeout 5m;
        ssl_protocols TLSv1.2 TLSv1.3;

        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        location / {
            proxy_pass http://localhost:9000;
        }

        #error_page  404              /404.html;

        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   /usr/share/nginx/html;
        }
    }
    ####

    vim run_nginx.sh
    ####
    docker run -d \
        --name nginx \
        --net=host \
        -v /mnt/sda1/docker/nginx/data/html:/usr/share/nginx/html \
        -v /mnt/sda1/docker/nginx/config/nginx:/etc/nginx \
        -v /mnt/sda1/docker/nginx/logs/nginx:/var/logs/nginx \
        -v /mnt/sda1/docker/nginx/ssl:/opt/ssl \
        nginx
    ####