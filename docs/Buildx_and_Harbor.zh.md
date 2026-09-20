[English](Buildx_and_Harbor.md) | [简体中文](Buildx_and_Harbor.zh.md)

<a id="buildx-and-harbor-on-the-cvgl-login-node"></a>
# CVGL 登录节点上的 Buildx 与 Harbor

本页说明 CVGL Linux 登录节点访问 Harbor 的 Buildx 路径。请先阅读较短的[自定义容器镜像操作指南](Custom_Containerized_Environment.zh.md)；需要诊断 TLS/DNS 阶段或创建独立 builder 时再使用本页。其他操作系统和 Docker 安装可能使用不同的证书和网络行为。

<a id="why-the-default-builder-needs-a-client-ca"></a>
## 默认 builder 为什么需要客户端 CA

登录节点上存在 registry 专用 CA 文件，因此 Docker Engine 操作可以信任 Harbor。但该证书不在登录节点默认系统根证书集合中。

Buildx 客户端通过 Docker 凭据 `ConfigFile` 创建 session auth provider，BuildKit auth provider 会发起 Harbor token 请求。因此，即使 Docker Engine 已经信任 registry，构建仍可能在 **Buildx 客户端进程**请求 `POST https://harbor.cvgl.lab/service/token` 时失败。

在这套 Linux 登录节点工作流中，使用 `SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab`。它会加入 registry 证书目录，同时保留这套 Go/Linux 环境正常的系统 CA 文件查找。Go 文档说明证书环境覆盖在其他平台上可能有不同表现。

保持 TLS 验证开启。

<a id="use-the-default-builder"></a>
## 使用默认 builder

常规构建：

```bash
IMAGE=harbor.cvgl.lab/<project>/<image>:<version-tag>
SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
  docker buildx build --builder default --load -t "$IMAGE" .
```

如需刷新基础镜像解析并重新运行构建步骤：

```bash
SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
  docker buildx build --builder default \
  --pull --no-cache --load -t "$IMAGE" .

docker run --rm "$IMAGE" <smoke-command>
```

`--load` 让 `docker run` 可以找到结果。不需要 `sudo`、重启 Docker daemon、更换 builder 或配置 insecure registry。

<a id="keep-the-legacy-fallback"></a>
## 保留 legacy fallback

如果默认 Buildx 路径失败，可以继续使用 legacy builder：

```bash
DOCKER_BUILDKIT=0 docker build -t "$IMAGE" .
```

把它作为诊断 Buildx 失败期间的显式 fallback。自动化中不要静默切换 builder。

<a id="create-an-independent-docker-container-builder"></a>
## 创建独立的 docker-container builder

需要固定 BuildKit 版本或使用 builder 专用配置时，可以使用独立 builder。要在当前部署中工作，它需要三个独立层次都正确：

1. `SSL_CERT_DIR`，供 Buildx 客户端请求 Harbor token；
2. BuildKit registry CA，供镜像 manifest 和 layer 流量使用；
3. 能解析 `harbor.cvgl.lab` 的 builder 容器 DNS。

<a id="1-builder-registry-ca"></a>
### 1. Builder registry CA

保存一个使用绝对路径的 TOML 文件，例如 `$PWD/cvgl-buildkitd.toml`：

```toml
[registry."harbor.cvgl.lab"]
  ca = ["/etc/docker/certs.d/harbor.cvgl.lab/cvgl.crt"]
```

Docker 的 BuildKit 文档说明，`--buildkitd-config` 引用的 registry CA 文件会被复制到 builder 的 `/etc/buildkit/certs` 下，builder 配置也会改写为这些路径。

<a id="2-builder-network-and-pinned-image"></a>
### 2. Builder network 与固定镜像

该部署通过 Linux 登录节点的 `/etc/hosts` 提供 `harbor.cvgl.lab`。创建 builder 时使用 `--driver-opt network=host`，让其 daemon 使用登录节点的 host-network 解析，而不是隔离的 bridge resolver。

创建 builder 时不要使用 `--use`，这样不会改变默认 builder：

```bash
BUILDKIT_CONFIG="$PWD/cvgl-buildkitd.toml"

docker buildx create \
  --name cvgl-harbor \
  --driver docker-container \
  --driver-opt image=moby/buildkit@sha256:28a898719c18a33f4e8000685287fa36fd0dd9560c6440227d3a732d79bb41d8 \
  --driver-opt network=host \
  --buildkitd-config "$BUILDKIT_CONFIG" \
  --bootstrap

docker buildx inspect cvgl-harbor
```

固定的 digest 标识此流程使用的 BuildKit `0.32.2` 镜像。请保留完整 digest；单独的 tag 可以移动。

<a id="3-build-explicitly"></a>
### 3. 显式构建

每次构建时显式选择独立 builder，并保留客户端 CA 环境：

```bash
SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
  docker buildx build --builder cvgl-harbor \
  --pull --no-cache --load -t "$IMAGE" .

docker run --rm "$IMAGE" <smoke-command>
```

`docker-container` driver 默认不会把结果载入 Docker 镜像存储，因此下一步需要 `docker run` 时应保留 `--load`。

<a id="network-options-are-not-interchangeable"></a>
## 网络选项不能互换

`docker buildx create` 上的 `--driver-opt network=host` 配置长期运行的 **builder 容器**网络，并在这套 Linux 登录节点配置中提供所需的主机解析。

`docker buildx build --network=host` 配置 Dockerfile `RUN` 指令的网络。它不会配置 builder daemon 自身的 DNS，不能替代 driver option。Docker 文档把它们定义为不同的控制项。

<a id="failure-stages"></a>
## 失败阶段

| 症状 | 失败阶段 | 处理方法 |
| --- | --- | --- |
| `POST https://harbor.cvgl.lab/service/token` 报告未知 CA | Buildx 客户端 auth provider | 在 `docker buildx build` 进程上设置 `SSL_CERT_DIR` |
| builder 日志中的 manifest 或 layer 请求报告未知 CA | BuildKit daemon 到 registry | 检查 `[registry."harbor.cvgl.lab"].ca`；如果独立 builder 配置已变化，重新创建它 |
| 独立 builder 中 `lookup harbor.cvgl.lab` 失败 | builder 容器 DNS | 对这套 Linux 登录节点配置，用 `--driver-opt network=host` 重新创建 |
| `unauthorized` 或 `denied` | Harbor 凭据或 project 授权 | 运行 `docker login` 并验证 project 访问权限 |
| 构建成功，但 `docker run` 找不到镜像 | 导出阶段 | 加上 `--load` |

各层互相独立。BuildKit 容器内的 CA 无法修复客户端 token POST，客户端 `SSL_CERT_DIR` 也无法修复 builder DNS。

<a id="primary-references"></a>
## 主要参考资料

- Docker：[配置 BuildKit](https://docs.docker.com/build/buildkit/configure/)，包括自动复制 registry CA。
- Docker：[`docker-container` driver](https://docs.docker.com/build/builders/drivers/docker-container/)，包括 builder `network` driver option 和 `--load` 行为。
- Docker：[`docker buildx build`](https://docs.docker.com/reference/cli/docker/buildx/build/)，其中 `--network` 作用于 Dockerfile `RUN` 指令。
- Go：[`crypto/x509.SystemCertPool`](https://pkg.go.dev/crypto/x509#SystemCertPool) 的证书环境行为。
- 特定版本源码：[Buildx `0.23.0` auth provider 构建](https://raw.githubusercontent.com/docker/buildx/v0.23.0/controller/build/build.go)和 [BuildKit `0.21.0` token 获取](https://raw.githubusercontent.com/moby/buildkit/v0.21.0/session/auth/authprovider/authprovider.go)。
