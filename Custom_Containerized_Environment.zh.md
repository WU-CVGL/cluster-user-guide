[English](Custom_Containerized_Environment.md) | [简体中文](Custom_Containerized_Environment.zh.md)

<a id="build-and-use-a-custom-container-image"></a>
# 构建和使用自定义容器镜像

本操作指南介绍当前 CVGL Harbor 工作流。它假定所选机器已经安装 Docker，
并且你有权在该机器上构建镜像。在受管理的主机上，更改 Docker 信任配置或
重启 Docker 服务之前，请联系管理员。

[`Example_Envs`](./Example_Envs/README.zh.md) 下的文件是历史参考。
使用前应审查并固定所有依赖；示例存在并不表示对应镜像目前仍能成功构建或运行。

<a id="1-choose-and-pin-a-base-image"></a>
## 1. 选择并固定基础镜像

优先使用由管理员认可、镜像到 `harbor.cvgl.lab` 的镜像。使用带版本的标签；
需要可复现性时，使用 digest：

```dockerfile
FROM harbor.cvgl.lab/<project>/<base-image>:<version-tag>
# Stronger reproducibility after the digest has been verified:
# FROM harbor.cvgl.lab/<project>/<base-image>@sha256:<digest>
```

避免使用 `latest` 等浮动标签。标签可以被移动，而 digest 标识已经审查过的
精确 manifest。

这里历史上的 RTX 4090 配方使用 CUDA 11.8 或更新的基础镜像。兼容性还取决于
框架、驱动、编译器和所有 CUDA 扩展，因此不能只检查 CUDA 版本。

<a id="2-trust-the-harbor-ca"></a>
## 2. 信任 Harbor CA

通过可信、已认证的渠道获取 Harbor CA 证书及其 SHA-256 指纹，例如直接向
系统管理员获取。不要在关闭 TLS 验证的情况下下载证书，再在没有通过其他渠道
核对指纹的情况下直接信任它。

安装前检查证书：

```bash
openssl x509 -in harbor-ca.crt -noout -subject -issuer -dates -fingerprint -sha256
```

将该指纹与管理员发布的值进行比较。在由你管理的 Linux Docker Engine 主机上，
将验证过的 CA 以 `.crt` 文件形式安装到与 registry 名称完全一致的目录下：

```bash
sudo install -d -m 0755 /etc/docker/certs.d/harbor.cvgl.lab
sudo install -m 0644 harbor-ca.crt /etc/docker/certs.d/harbor.cvgl.lab/ca.crt
sudo systemctl restart docker
```

在受管理的集群主机上，不要自行覆盖已有证书或重启 Docker；请让管理员检查或
修复信任配置。Docker 会把该目录中的每个 `*.crt` 文件作为 CA 根证书。
如果已有管理员提供的 `server.crt`，且该文件确实是验证过的 CA 证书，那么这个
文件名同样有效。Docker Desktop 和 rootless Docker 使用不同的证书位置；请根据
[Docker registry 证书文档](https://docs.docker.com/engine/security/certificates/)
完成对应安装。

当 TLS 信任正常、但没有提供 Harbor 凭据时，下面的只读探测预期返回 HTTP
`401 Unauthorized`：

```bash
curl --silent --show-error --output /dev/null --write-out '%{http_code}\n' \
  --cacert harbor-ca.crt https://harbor.cvgl.lab/v2/
```

<a id="3-log-in-without-exposing-the-password"></a>
## 3. 登录且不暴露密码

交互使用时，让 Docker 提示输入密码：

```bash
docker login harbor.cvgl.lab --username <username>
```

在受控的自动化环境中，通过标准输入传递 secret。不要使用
`docker login -p ...`，因为密码会成为命令行参数：

```bash
printf '%s' "$HARBOR_PASSWORD" |
  docker login harbor.cvgl.lab --username <username> --password-stdin
```

Docker 可能会把得到的凭据保存在 `~/.docker/config.json`；条件允许时请配置
Docker credential store。有关 credential store 和 `--password-stdin` 的行为，
请参阅 [`docker login`](https://docs.docker.com/reference/cli/docker/login/)。

<a id="4-write-the-dockerfile"></a>
## 4. 编写 Dockerfile

保持较小的构建上下文，并使用 `.dockerignore`。下面是在已认可基础镜像上扩展的
最小示例：

```dockerfile
FROM harbor.cvgl.lab/<project>/<base-image>:<version-tag>

ARG DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PIP_NO_CACHE_DIR=1

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --requirement /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt
```

固定 Python 包和源码 checkout。包含 shell 运算符的 requirement 必须加引号，
例如 `python -m pip install "nerfstudio>=1.0"`，避免 `>` 被解释成 shell
重定向。不要通过 build argument 传递 token 或密码：build argument 和镜像层
都不是 secret store。

<a id="5-build-with-the-current-compatible-path"></a>
## 5. 使用当前兼容路径构建

对于当前使用自签 CA 的 CVGL Harbor 部署，受支持的兼容路径是 legacy Docker
builder：

```bash
IMAGE=harbor.cvgl.lab/<project>/<image>:<version-tag>
DOCKER_BUILDKIT=0 docker build -t "$IMAGE" .
```

这条路径必须保留 `DOCKER_BUILDKIT=0`。末尾的 `.` 是构建上下文。如果构建过程
本身需要站点代理，请使用管理员提供的代理 URL，并且只传递不含 secret 的代理
地址：

```bash
DOCKER_BUILDKIT=0 docker build \
  --build-arg http_proxy=<proxy-url> \
  --build-arg https_proxy=<proxy-url> \
  -t "$IMAGE" .
```

如果 Docker daemon 拉取基础镜像时需要代理，请联系管理员配置。build argument
只配置临时构建容器中的 `RUN` 步骤，不会配置 Docker daemon。

<a id="optional-unverified-buildkit-migration"></a>
### 可选且尚未验证的 BuildKit 迁移

BuildKit 尚未在这个 Harbor 部署上通过验证。现在不要替换上面的兼容命令。
未来的迁移应使用一个显式配置 registry CA 的独立 `docker-container` builder；
不要把 `--buildkitd-config` 流程直接套用到已有的默认 `docker` driver。

独立测试 builder 的配置示例：

```toml
# /absolute/path/to/cvgl-buildkitd.toml
[registry."harbor.cvgl.lab"]
  ca = ["/absolute/path/to/verified-harbor-ca.crt"]
```

在可以运行测试构建的机器上，创建并检查这个隔离 builder，然后运行一次不推送的
测试构建：

```bash
docker buildx create \
  --name cvgl-harbor-test \
  --driver docker-container \
  --buildkitd-config /absolute/path/to/cvgl-buildkitd.toml \
  --bootstrap

docker buildx inspect cvgl-harbor-test
docker buildx build --builder cvgl-harbor-test --load -t "$IMAGE" .
```

Docker 在
[配置 BuildKit](https://docs.docker.com/build/buildkit/configure/) 中说明了 CA
如何被复制进 `docker-container` builder。在基础镜像拉取和完整的不推送构建都
验证成功之前，应把这一路径视为迁移实验。

<a id="6-tag-and-push"></a>
## 6. 添加标签并推送

如果本地构建使用了不同的标签，请添加完整的 Harbor 引用，然后显式推送：

```bash
docker tag <local-image>:<local-tag> \
  harbor.cvgl.lab/<project>/<image>:<version-tag>
docker push harbor.cvgl.lab/<project>/<image>:<version-tag>
```

镜像内容变化时使用新的、有意义的版本标签。记录 `docker push` 输出或 Harbor
显示的 digest。不要覆盖发布标签，保持标签稳定；需要可复现作业时使用已记录的
digest。

<a id="7-use-the-image-with-determined"></a>
## 7. 在 Determined 中使用镜像

在任务配置中引用已推送的标签或验证过的 digest：

```yaml
environment:
  image: harbor.cvgl.lab/<project>/<image>:<version-tag>
```

任务规划和提交请参阅 [Determined compute 指南](./Determined_AI_User_Guide.zh.md)
和 [MCP 工作流](./Agent_Workflow.zh.md)。代码、数据集、checkpoint 和输出请遵循
[共享存储指南](./Shared_Storage.zh.md)。镜像应保存运行环境；不断变化的数据集和
运行产物应放在共享存储上。

<a id="troubleshooting"></a>
## 故障排查

- `x509: certificate signed by unknown authority`：检查 CA 指纹、证书扩展名、
  registry 目录名以及当前 Docker 安装所需的证书位置。不要启用
  insecure-registry。
- `unauthorized` 或 `denied`：重新登录，并确认你有权访问对应 Harbor project。
  TLS 信任与 registry 授权是两个独立的检查。
- BuildKit 拉取失败，但兼容构建可用：继续使用 `DOCKER_BUILDKIT=0`；隔离的
  BuildKit CA 路径仍未验证。
- package constraint 产生了类似 `=0.16.0` 的文件：给传入 shell 的完整
  requirement 加引号。
- 作业看不到代码或输出：检查 Determined bind mount，并把工作负载放在已认可的
  共享存储根目录下。
