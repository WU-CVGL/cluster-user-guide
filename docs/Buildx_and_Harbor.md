[English](Buildx_and_Harbor.md) | [简体中文](Buildx_and_Harbor.zh.md)

# Buildx and Harbor on the CVGL login node

This page explains the verified Buildx paths for the CVGL Harbor deployment. Start with the shorter [custom container image HOWTO](Custom_Containerized_Environment.md); use this page when diagnosing TLS/DNS stages or creating an isolated builder.

## Verified scope

The following was verified on `cvglloginnode` on 2026-09-20:

| Component | Verified value |
| --- | --- |
| Docker Engine | `28.1.1` |
| Buildx | `0.23.0` |
| Default builder | `docker` driver, bundled BuildKit `0.21.0` |
| Independent builder | `docker-container` driver, BuildKit `0.32.2` image pinned below |
| Harbor CA file | `/etc/docker/certs.d/harbor.cvgl.lab/cvgl.crt` |

Both builder paths successfully resolved a Harbor base image, executed a Dockerfile `RUN` step, loaded the result with `--load`, and ran the image with `docker run`. `--pull` refreshed base-image metadata and `--no-cache` reran build steps; neither option guarantees that existing content layers are downloaded again. The independent builder downloaded new layers during verification, while the default builder reused layers already present from the legacy build. Push, multi-platform output, other builders, and other operating systems were not tested.

## Why the default builder needs a client CA

The registry-specific CA file exists on the login node, so Docker Engine operations can trust Harbor. It is not part of the login node's default system root set, however.

With Buildx `0.23.0`, the Buildx client creates the session auth provider from Docker's credential `ConfigFile`. BuildKit `0.21.0` performs the Harbor token request through that auth provider. Therefore a build can fail on `POST https://harbor.cvgl.lab/service/token` in the **Buildx client process** even when Docker Engine already trusts the registry.

On the verified Linux login node, setting `SSL_CERT_FILE` to the Harbor CA worked. The preferred form is `SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab`: it adds the registry certificate directory while retaining the normal system CA file lookup in this tested Go/Linux environment. Treat this as deployment-specific; Go documents different platform behavior for certificate environment overrides.

Keep TLS verification enabled.

## Use the verified default builder

For a normal build:

```bash
IMAGE=harbor.cvgl.lab/<project>/<image>:<version-tag>
SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
  docker buildx build --builder default --load -t "$IMAGE" .
```

For a deliberate validation that refreshes base-image resolution and reruns build steps:

```bash
SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
  docker buildx build --builder default \
  --pull --no-cache --load -t "$IMAGE" .

docker run --rm "$IMAGE" <smoke-command>
```

`--load` makes the result available to `docker run`. No `sudo`, Docker daemon restart, builder replacement, or insecure-registry setting is needed.

## Keep the legacy fallback

The legacy builder remains available if the verified Buildx path regresses:

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

The default bridge-network builder could not resolve `harbor.cvgl.lab` because this deployment supplies the name through the login node's `/etc/hosts`. With Docker `28.1.1` on this Linux host, `--driver-opt network=host` gave the builder the verified host resolution.

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

The pinned image resolved to BuildKit `0.32.2` during verification. Keep the digest intact; a tag alone can move.

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

`--driver-opt network=host` on `docker buildx create` configures the long-lived **builder container** network. It fixed builder-daemon DNS in the verified login-node environment.

`docker buildx build --network=host` configures networking for Dockerfile `RUN` instructions. It does not configure the builder daemon's own DNS and is not a substitute for the driver option. Docker documents these as separate controls.

## Failure stages

| Symptom | Failing stage | Action |
| --- | --- | --- |
| `POST https://harbor.cvgl.lab/service/token` reports unknown CA | Buildx client auth provider | Set `SSL_CERT_DIR` on the `docker buildx build` process |
| Manifest or layer request reports unknown CA in builder logs | BuildKit daemon to registry | Check `[registry."harbor.cvgl.lab"].ca` and recreate the isolated builder if its config changed |
| `lookup harbor.cvgl.lab` fails in an isolated builder | Builder-container DNS | On this verified Linux host, recreate it with `--driver-opt network=host` |
| `unauthorized` or `denied` | Harbor credentials or project authorization | Run `docker login` and verify project access |
| Build succeeds but `docker run` cannot find the image | Export step | Add `--load` |

Each layer is independent. A CA inside the BuildKit container does not fix the client-side token POST, and client `SSL_CERT_DIR` does not fix builder DNS.

## Primary references

- Docker: [Configure BuildKit](https://docs.docker.com/build/buildkit/configure/), including automatic registry CA copying.
- Docker: [`docker-container` driver](https://docs.docker.com/build/builders/drivers/docker-container/), including the builder `network` driver option and `--load` behavior.
- Docker: [`docker buildx build`](https://docs.docker.com/reference/cli/docker/buildx/build/), where `--network` applies to Dockerfile `RUN` instructions.
- Go: [`crypto/x509.SystemCertPool`](https://pkg.go.dev/crypto/x509#SystemCertPool) certificate environment behavior.
- Version-specific source: [Buildx `0.23.0` auth-provider construction](https://raw.githubusercontent.com/docker/buildx/v0.23.0/controller/build/build.go) and [BuildKit `0.21.0` token fetching](https://raw.githubusercontent.com/moby/buildkit/v0.21.0/session/auth/authprovider/authprovider.go).
