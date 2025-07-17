<h1 align="center">Custom Containerized Deep Learning Environment<br>
with Docker and Harbor </h1>

- [For Beginners: build FROM a base image](#for-beginners-build-from-a-base-image)
  - [Set up the CVGL CA certificate to use our Harbor registry](#set-up-the-cvgl-ca-certificate-to-use-our-harbor-registry)
  - [Example](#example)
- [Upload the custom image](#upload-the-custom-image)
- [Use the custom image](#use-the-custom-image)
- [Advanced: build an image from scratch](#advanced-build-an-image-from-scratch)
- [Proxy](#proxy)
  - [Set up proxy for the docker daemon](#set-up-proxy-for-the-docker-daemon)
  - [Set up proxy in the temporary building container](#set-up-proxy-in-the-temporary-building-container)

# For Beginners: build FROM a base image

*Determined AI* provides [*Docker* images](https://hub.docker.com/r/determinedai/environments/tags) that includes common deep-learning libraries and frameworks. You can also [develop your custom image](https://gpu.cvgl.lab/docs/prepare-environment/custom-env.html) based on your project dependency.

For beginners, it is recommended that custom images use one of the Determined AI's official images as a base image, using the `FROM` instruction.

## Set up the CVGL CA certificate to use our Harbor registry

Instead of pulling determinedai's images from Docker Hub (which requires setting up proxy now), you can pull them from our Harbor registry.

Make sure you have configured your `hosts` file with the following settings:

```text
10.0.1.68 cvgl.lab
10.0.1.68 harbor.cvgl.lab
```

Check out [here](https://harbor.cvgl.lab/harbor/projects) to see the available images.

We have mirrored some of the determined ai's environments in `harbor`. [Here is the link](https://harbor.cvgl.lab/harbor/projects/3/repositories/environments).

You can also ask the system admin to add or update the images.

If you want to use the images from the docker hub, you will need to [use the proxy service](#proxy).

To use our Harbor registry, you need to complete the following setup:

```bash
sudo mkdir -p /etc/docker/certs.d/harbor.cvgl.lab
cd /etc/docker/certs.d/harbor.cvgl.lab
sudo wget https://cvgl.lab/cvgl.crt --no-check-certificate
sudo systemctl restart docker
```

This configures the CA certificate for Docker.

Then log in to our Harbor registry:

```bash
docker login -u <username> -p <password> harbor.cvgl.lab    # You only need to login once
```

Now edit the first `FROM` line in the `Dockerfile`, and change the base image to some existing image in the Harbor registry, for example:

```dockerfile
FROM harbor.cvgl.lab/determinedai/environments:cuda-11.8-pytorch-2.0-gpu-mpi-0.31.1
```

## Example

Here is an example: Suppose you have `environment.yaml` for creating the `conda` environment, `pip_requirements.txt` for `pip` requirements and some `apt` packages that need to be installed.

> Before proceeding to build your custom Docker image, you need to [install Docker](https://docs.docker.com/engine/install/), or you can choose the *easier* way: build it on the **login-node**.

Put these files in a folder, and create a `Dockerfile` with the following contents:

```Dockerfile
# Determined Image
FROM harbor.cvgl.lab/determinedai/environments:cuda-11.8-pytorch-2.0-gpu-mpi-0.31.1
# Some important environment variables in Dockerfile
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai LANG=C.UTF-8 LC_ALL=C.UTF-8 PIP_NO_CACHE_DIR=1

# Custom Configuration
RUN sed -i  "s/archive.ubuntu.com/mirrors.ustc.edu.cn/g" /etc/apt/sources.list && \
    sed -i  "s/security.ubuntu.com/mirrors.ustc.edu.cn/g" /etc/apt/sources.list && \
    rm -f /etc/apt/sources.list.d/* && \
    apt-get update && \
    apt-get -y install tzdata && \
    apt-get install -y unzip python-opencv graphviz
COPY environment.yml /tmp/environment.yml
COPY pip_requirements.txt /tmp/pip_requirements.txt
RUN conda install -n base libarchive -c main --force-reinstall --yes
RUN conda env update --name base --file /tmp/environment.yml
RUN conda clean --all --force-pkgs-dirs --yes
RUN eval "$(conda shell.bash hook)" && \
    conda activate base && \
    pip config set global.index-url https://mirrors.bfsu.edu.cn/pypi/web/simple &&\
    pip install --requirement /tmp/pip_requirements.txt
```

If you want to adapt your custom containerized environment for NVIDIA RTX 4090, `CUDA version >= 11.8` is required.

Here are some other examples:

[svox2](./Example_Envs/svox2/)

[lietorch-opencv](./Example_Envs/lietorch-opencv/)

Notice that we are using the `apt` mirror by `ustc.edu.cn` and the `pip` mirror by `bfsu.edu.cn`. They are currently fast and thus recommended by the system admin.

To build the image, use the following command:

```bash
DOCKER_BUILDKIT=0 docker build -t my_image:v1.0 .
```

where `my_image` is your image name, and `v1.0` is the image tag that usually contains descriptions and version information. `DOCKER_BUILDKIT=0` is needed if you are using private Docker registry (i.e. our Harbor) [[Reference]](https://stackoverflow.com/questions/75766469/docker-build-cannot-pull-base-image-from-private-docker-registry-that-requires).

Don't forget the dot "." at the end of the command (which represents *the current directory* that contains the Dockerfile)!

# Upload the custom image

Instead of pushing the image to Docker Hub (which has already been blocked), it is recommended to use the private Harbor registry: `harbor.cvgl.lab`.

You need to ask the system admin to create your Harbor user account. Once you have logged in, you can check out the [public library](https://harbor.cvgl.lab/harbor/projects/1/repositories):

<img src="./Custom_Containerized_Environment/harbor-library.png" alt="Harbor library" style="width:40vw;"/>

Note that instead of using the default `library`, you can also create your own *project* in Harbor.

Now you can create your custom Docker images on the login node or your PC following the instructions above, and then push the image to the Harbor registry. For instance:

```bash
docker login -u <username> -p <password> harbor.cvgl.lab    # You only need to login once
docker tag my_image:v1.0  harbor.cvgl.lab/library/my_image:v1.0
docker push harbor.cvgl.lab/library/my_image:v1.0
```

In the first line, replace `<username>` with your username and `<password>` with your password.

In the second line, add the prefix `harbor.cvgl.lab/library/` to your image. Don't worry, this process does not occupy additional storage.

In the third line, push your new tagged image.

# Use the custom image

In the Determined AI configuration `.yaml` file (as mentioned in [the previous tutorial](./Determined_AI_User_Guide.md#task-configuration-template)), use the newly tagged image (like `harbor.cvgl.lab/library/my_image:v1.0` above) to tell the system to use your new image as the task environment.

Also note that every time you update an image, you need to change the image name, otherwise the system will not be able to detect the image update (probably because it only uses the image name as detection, not its checksum).

# Advanced: build an image from scratch

To make our life easier, we will build our custom image FROM NVIDIA's base image. You can use the minimum template we provide: [determined-minimum](https://github.com/LingzheZhao/determinedai-container-scripts)

Note that for RTX 4090, we need `CUDA` version >= `11.8`, thus you need to use the base image from [NGC/CUDA](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/cuda) with tags >= 11.8, or [NGC/Pytorch](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch) with tags >= 22.09.

Here are some examples tested on RTX 4090:

1. nerf-env [[Dockerfile]](./Example_Envs/nerf-env/) [[Harbor]](https://harbor.cvgl.lab/harbor/projects/1/repositories/nerf_env_test/artifacts-tab/artifacts/sha256:fd1376632bd15ea92eb9791723e95fab833f4f30185a9a8c3f765d158713bc60)

2. nerfstudio [[Dockerfile]](./Example_Envs/nerfstudio/) [[Harbor - nerfstudio]](https://harbor.cvgl.lab/harbor/projects/1/repositories/zlz-nerfstudio/artifacts-tab) 

# Proxy

## Set up proxy for the docker daemon

You need to set up proxy for the docker daemon in order to pull images from the docker hub (i.e. `docker pull <image>` command or `FROM <image>` in the first line of your `Dockerfile`) since it has been blocked.

The status of our public proxies can be monitored here: [Grafana - v2ray-dashboard](https://grafana.cvgl.lab/d/CCSvIIEZz/v2ray-dashboard)

1) To proceed, recursively create the folder:

    ```sh
    sudo mkdir -p /etc/systemd/system/docker.service.d
    ```

2) Add environment variables to the configuration file `/etc/systemd/system/docker.service.d/proxy.conf`:

    ```conf
    [Service]
    Environment="HTTP_PROXY=http://10.0.1.68:28889"
    Environment="HTTPS_PROXY=http://10.0.1.68:28889"
    Environment="NO_PROXY=localhost,127.0.0.1,nvcr.io,aliyuncs.com,edu.cn,cvgl.lab"
    ```

    You can change `10.0.1.68` and `8889` to the other proxy address and port respectively.

    Note that the `http` is intentionally used in `HTTPS_PROXY` - this is how most HTTP proxies work.

3) Update configuration and restart `Docker`:

    ```sh
    systemctl daemon-reload
    systemctl restart docker
    ```

4) Check the proxy:

    ```sh
    docker info
    ```

## Set up proxy in the temporary building container

If you also need international internet access during the Dockerfile building process, you can add build arguments to use the public proxy services:

```bash
DOCKER_BUILDKIT=0 docker build -t my_image:v1.0 --build-arg http_proxy=http://10.0.1.68:28889 --build-arg https_proxy=http://10.0.1.68:28889 .
```
