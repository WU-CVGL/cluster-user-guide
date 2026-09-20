[English](Buildx_and_Harbor.md) | [简体中文](Buildx_and_Harbor.zh.md)

# Buildx and Harbor on the CVGL login node

This page explains the Buildx paths for Harbor on the CVGL Linux login node. Start with the shorter [custom container image HOWTO](Custom_Containerized_Environment.md); use this page when diagnosing TLS/DNS stages or creating an isolated builder. Other operating systems and Docker installations can use different certificate and network behavior.

## Why the default builder needs a client CA

The registry-specific CA file exists on the login node, so Docker Engine operations can trust Harbor. It is not part of the login node's default system root set, however.

The Buildx client creates the session auth provider from Docker's credential `ConfigFile`, and the BuildKit auth provider performs the Harbor token request. Therefore a build can fail on `POST https://harbor.cvgl.lab/service/token` in the **Buildx client process** even when Docker Engine already trusts the registry.

For this Linux login-node workflow, use `SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab`. It adds the registry certificate directory while retaining the normal system CA file lookup for this Go/Linux environment. Go documents different behavior for certificate environment overrides on other platforms.

Keep TLS verification enabled.

## Use the default builder

For a normal build:

```bash
IMAGE=harbor.cvgl.lab/<project>/<image>:<version-tag>
SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
  docker buildx build --builder default --load -t "$IMAGE" .
```

To refresh base-image resolution and rerun build steps:

```bash
SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
  docker buildx build --builder default \
  --pull --no-cache --load -t "$IMAGE" .

docker run --rm "$IMAGE" <smoke-command>
```

`--load` makes the result available to `docker run`. No `sudo`, Docker daemon restart, builder replacement, or insecure-registry setting is needed.

## Keep the legacy fallback

The legacy builder remains available if the default Buildx path fails:

```bash
DOCKER_BUILDKIT=0 docker build -t "$IMAGE" .
```

Use this as an explicit fallback while diagnosing the Buildx failure. Do not silently switch builders in automation.

## Create an independent docker-container builder

An isolated builder is useful when you need a pinned BuildKit version or builder-specific configuration. It needs three separate layers to work with this deployment:

1. `SSL_CERT_DIR` for the Buildx client's Harbor token request;
2. a BuildKit registry CA for image manifest and layer traffic;
3. builder-container DNS that resolves `harbor.cvgl.lab`.

### 1. Builder registry CA

Save an absolute-path TOML file such as `$PWD/cvgl-buildkitd.toml`:

```toml
[registry."harbor.cvgl.lab"]
  ca = ["/etc/docker/certs.d/harbor.cvgl.lab/cvgl.crt"]
```

Docker's BuildKit documentation states that registry CA files referenced by `--buildkitd-config` are copied into the builder under `/etc/buildkit/certs` and the builder configuration is rewritten to those paths.

### 2. Builder network and pinned image

This deployment supplies `harbor.cvgl.lab` through the Linux login node's `/etc/hosts`. Create the builder with `--driver-opt network=host` so its daemon uses the login node's host-network resolution instead of an isolated bridge resolver.

Create the builder without `--use`, so the default builder remains unchanged:

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

The pinned digest identifies the BuildKit `0.32.2` image used by this procedure. Keep the digest intact; a tag alone can move.

### 3. Build explicitly

Select the isolated builder on each build command and keep the client CA environment:

```bash
SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
  docker buildx build --builder cvgl-harbor \
  --pull --no-cache --load -t "$IMAGE" .

docker run --rm "$IMAGE" <smoke-command>
```

The `docker-container` driver does not load results into the Docker image store by default, so retain `--load` when the next step is `docker run`.

## Network options are not interchangeable

`--driver-opt network=host` on `docker buildx create` configures the long-lived **builder container** network and supplies the required host resolution in this Linux login-node setup.

`docker buildx build --network=host` configures networking for Dockerfile `RUN` instructions. It does not configure the builder daemon's own DNS and is not a substitute for the driver option. Docker documents these as separate controls.

## Failure stages

| Symptom | Failing stage | Action |
| --- | --- | --- |
| `POST https://harbor.cvgl.lab/service/token` reports unknown CA | Buildx client auth provider | Set `SSL_CERT_DIR` on the `docker buildx build` process |
| Manifest or layer request reports unknown CA in builder logs | BuildKit daemon to registry | Check `[registry."harbor.cvgl.lab"].ca` and recreate the isolated builder if its config changed |
| `lookup harbor.cvgl.lab` fails in an isolated builder | Builder-container DNS | For this Linux login-node setup, recreate it with `--driver-opt network=host` |
| `unauthorized` or `denied` | Harbor credentials or project authorization | Run `docker login` and verify project access |
| Build succeeds but `docker run` cannot find the image | Export step | Add `--load` |

Each layer is independent. A CA inside the BuildKit container does not fix the client-side token POST, and client `SSL_CERT_DIR` does not fix builder DNS.

## Primary references

- Docker: [Configure BuildKit](https://docs.docker.com/build/buildkit/configure/), including automatic registry CA copying.
- Docker: [`docker-container` driver](https://docs.docker.com/build/builders/drivers/docker-container/), including the builder `network` driver option and `--load` behavior.
- Docker: [`docker buildx build`](https://docs.docker.com/reference/cli/docker/buildx/build/), where `--network` applies to Dockerfile `RUN` instructions.
- Go: [`crypto/x509.SystemCertPool`](https://pkg.go.dev/crypto/x509#SystemCertPool) certificate environment behavior.
- Version-specific source: [Buildx `0.23.0` auth-provider construction](https://raw.githubusercontent.com/docker/buildx/v0.23.0/controller/build/build.go) and [BuildKit `0.21.0` token fetching](https://raw.githubusercontent.com/moby/buildkit/v0.21.0/session/auth/authprovider/authprovider.go).
