[English](Custom_Containerized_Environment.md) | [简体中文](Custom_Containerized_Environment.zh.md)

<a id="build-and-use-a-custom-container-image"></a>
# 构建和使用自定义容器镜像

本操作指南介绍常规的 CVGL Harbor 工作流。它假定所选机器已经安装 Docker，并且你有权在该机器上构建镜像。

[`examples/environments`](../examples/environments/README.zh.md) 下的文件是历史参考。使用前应审查并固定所有依赖；示例存在并不表示对应镜像目前仍能成功构建或运行。

<a id="1-choose-and-pin-a-base-image"></a>
## 1. 选择并固定基础镜像

优先使用由管理员认可、镜像到 `harbor.cvgl.lab` 的镜像。使用带版本的标签；需要可复现性时使用 digest：

```dockerfile
FROM harbor.cvgl.lab/<project>/<base-image>:<version-tag>
# Stronger reproducibility with a pinned digest:
# FROM harbor.cvgl.lab/<project>/<base-image>@sha256:<digest>
```

避免使用 `latest` 等浮动标签。兼容性取决于框架、驱动、编译器、CUDA 版本以及所有已编译扩展。

<a id="2-trust-the-harbor-ca"></a>
## 2. 信任 Harbor CA

登录节点已经在 `/etc/docker/certs.d/harbor.cvgl.lab/cvgl.crt` 安装 Harbor 证书；不要重复安装，也不要重启共享 Docker daemon。在个人设备上，下载 [`cvgl.crt`](https://cvgl.lab/cvgl.crt)，并按照[集群入门](Getting_started.zh.md#3-enroll-the-cluster-ca-when-required)操作。

对于个人 Linux 机器上的 Docker Engine，还要把证书放进 Docker 为该 registry 使用的证书目录：

```bash
sudo install -d -m 0755 /etc/docker/certs.d/harbor.cvgl.lab
sudo install -m 0644 cvgl.crt /etc/docker/certs.d/harbor.cvgl.lab/cvgl.crt
```

Docker Desktop 和 rootless Docker 使用不同的位置；请根据 [Docker registry 证书文档](https://docs.docker.com/engine/security/certificates/)完成对应安装。

<a id="3-log-in-without-exposing-the-password"></a>
## 3. 登录且不暴露密码

交互使用时，让 Docker 提示输入密码：

```bash
docker login harbor.cvgl.lab --username <username>
```

在受控的自动化环境中，通过标准输入而不是命令行参数传递 secret：

```bash
printf '%s' "$HARBOR_PASSWORD" |
  docker login harbor.cvgl.lab --username <username> --password-stdin
```

Docker 可能会把凭据保存在 `~/.docker/config.json`；条件允许时请配置 credential store。TLS 信任与 Harbor 授权是两个独立检查。

<a id="4-write-the-dockerfile"></a>
## 4. 编写 Dockerfile

保持较小的构建上下文，并使用 `.dockerignore`。下面是在已认可基础镜像上扩展的最小示例：

```dockerfile
FROM harbor.cvgl.lab/<project>/<base-image>:<version-tag>

ARG DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PIP_NO_CACHE_DIR=1

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --requirement /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt
```

固定软件包和源码 checkout。包含 shell 运算符的 requirement 必须加引号，例如 `python -m pip install "nerfstudio>=1.0"`。不要通过 build argument 传递 token 或密码：build argument 和镜像层都不是 secret store。

<a id="5-build-on-the-login-node-with-buildx"></a>
## 5. 在登录节点上使用 Buildx 构建

在登录节点上，使用默认 Buildx builder，并向 Buildx 客户端进程添加 Harbor CA 目录：

```bash
IMAGE=harbor.cvgl.lab/<project>/<image>:<version-tag>
SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
  docker buildx build --builder default --load -t "$IMAGE" .
```

`--load` 会把结果放入本地 Docker 镜像存储。该命令不需要 `sudo`、重启 Docker 或绕过 TLS。

CA/DNS 根因和高级 builder 设置请参阅 [Buildx 与 Harbor](Buildx_and_Harbor.zh.md)。

如果 Dockerfile `RUN` 步骤需要站点代理，请把当前获准使用的 URL 作为非 secret build argument 传入：

```bash
SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
  docker buildx build --builder default --load \
  --build-arg http_proxy=<proxy-url> \
  --build-arg https_proxy=<proxy-url> \
  -t "$IMAGE" .
```

Build argument 只配置 `RUN` 步骤；它不会配置 Docker Engine，也不会配置 Buildx 客户端的基础镜像/token 流量。请参阅[网络与远程访问](Network_and_Remote_Access.zh.md#proxies-and-mirrors)。

<a id="legacy-fallback"></a>
### Legacy fallback

如果 Buildx 命令失败，legacy builder 仍可作为兼容 fallback：

```bash
DOCKER_BUILDKIT=0 docker build -t "$IMAGE" .
```

应诊断 Buildx 的失败阶段，而不是改变 TLS 或认证语义。

<a id="6-tag-and-push"></a>
## 6. 添加标签并推送

如果本地构建使用了不同的标签，请添加完整的 Harbor 引用，然后显式推送：

```bash
docker tag <local-image>:<local-tag> \
  harbor.cvgl.lab/<project>/<image>:<version-tag>
docker push harbor.cvgl.lab/<project>/<image>:<version-tag>
```

镜像内容变化时使用新的、有意义的版本标签，确认项目权限，并记录得到的 digest。

<a id="7-use-the-image-with-determined"></a>
## 7. 在 Determined 中使用镜像

在任务配置中引用已推送的标签或固定的 digest：

```yaml
environment:
  image: harbor.cvgl.lab/<project>/<image>:<version-tag>
```

原生任务规划和提交请参阅 [Determined compute 指南](Determined_AI_User_Guide.zh.md)，agent 辅助操作请参阅规范的 [MCP 工作流](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/agent-workflow.zh.md)。代码、数据集、checkpoint 和输出请遵循[共享存储](Shared_Storage.zh.md)。镜像应保存运行环境；不断变化的数据和运行产物应放在共享存储上。

<a id="troubleshooting"></a>
## 故障排查

- 默认 Buildx 构建在请求 `https://harbor.cvgl.lab/service/token` 时报告 `x509: certificate signed by unknown authority`：使用文档中的 `SSL_CERT_DIR` 运行该 Buildx 命令。
- `unauthorized` 或 `denied`：重新运行 `docker login` 并确认你有权访问对应 Harbor project。这是授权失败，不是 CA 失败。
- builder 报告 DNS lookup 失败或独立 BuildKit registry 错误：使用 [Buildx 与 Harbor](Buildx_and_Harbor.zh.md#failure-stages)中的三层诊断。
- package constraint 产生类似 `=0.16.0` 的文件：给传入 shell 的完整 requirement 加引号。
- Determined 任务看不到代码或输出：检查 bind mount，并使用已认可的共享存储根目录。
