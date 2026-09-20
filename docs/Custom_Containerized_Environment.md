[English](Custom_Containerized_Environment.md) | [简体中文](Custom_Containerized_Environment.zh.md)

# Build and use a custom container image

This HOWTO covers the normal CVGL Harbor workflow. It assumes Docker is installed and you are allowed to build images on the selected machine.

The files under [`examples/environments`](../examples/environments/README.md) are historical references. Review and pin every dependency before using one; an example's presence does not mean its image currently builds or runs.

## 1. Choose and pin a base image

Prefer an administrator-approved image mirrored in `harbor.cvgl.lab`. Use a versioned tag, and use a digest when reproducibility matters:

```dockerfile
FROM harbor.cvgl.lab/<project>/<base-image>:<version-tag>
# Stronger reproducibility with a pinned digest:
# FROM harbor.cvgl.lab/<project>/<base-image>@sha256:<digest>
```

Avoid floating tags such as `latest`. Compatibility depends on the framework, driver, compiler, CUDA version, and any compiled extensions.

## 2. Trust the Harbor CA

The login node already has the Harbor certificate at `/etc/docker/certs.d/harbor.cvgl.lab/cvgl.crt`; do not reinstall it or restart the shared Docker daemon. On a personal device, download [`cvgl.crt`](https://cvgl.lab/cvgl.crt) and follow [Getting started](Getting_started.md#3-enroll-the-cluster-ca-when-required).

For Docker Engine on a personal Linux machine, also place the certificate in Docker's registry-specific directory:

```bash
sudo install -d -m 0755 /etc/docker/certs.d/harbor.cvgl.lab
sudo install -m 0644 cvgl.crt /etc/docker/certs.d/harbor.cvgl.lab/cvgl.crt
```

Docker Desktop and rootless Docker use different locations; follow the [Docker registry certificate documentation](https://docs.docker.com/engine/security/certificates/) for that installation.

## 3. Log in without exposing the password

For interactive use, let Docker prompt for the password:

```bash
docker login harbor.cvgl.lab --username <username>
```

For controlled automation, pass a secret through standard input rather than a command-line argument:

```bash
printf '%s' "$HARBOR_PASSWORD" |
  docker login harbor.cvgl.lab --username <username> --password-stdin
```

Docker may store the credential in `~/.docker/config.json`; configure a credential store where available. TLS trust and Harbor authorization are separate checks.

## 4. Write the Dockerfile

Keep the build context small and use a `.dockerignore`. A minimal extension of an approved base looks like this:

```dockerfile
FROM harbor.cvgl.lab/<project>/<base-image>:<version-tag>

ARG DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PIP_NO_CACHE_DIR=1

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --requirement /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt
```

Pin packages and source checkouts. Quote requirements containing shell operators, for example `python -m pip install "nerfstudio>=1.0"`. Do not pass tokens or passwords as build arguments: build arguments and image layers are not secret stores.

## 5. Build on the login node with Buildx

On the login node, use the default Buildx builder and add the Harbor CA directory to the Buildx client process:

```bash
IMAGE=harbor.cvgl.lab/<project>/<image>:<version-tag>
SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
  docker buildx build --builder default --load -t "$IMAGE" .
```

`--load` places the result in the local Docker image store. This command needs no `sudo`, Docker restart, or TLS bypass.

See [Buildx and Harbor](Buildx_and_Harbor.md) for the CA/DNS root cause and advanced builder setup.

If Dockerfile `RUN` steps need the site proxy, use the current approved URL as a non-secret build argument:

```bash
SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
  docker buildx build --builder default --load \
  --build-arg http_proxy=<proxy-url> \
  --build-arg https_proxy=<proxy-url> \
  -t "$IMAGE" .
```

Build arguments configure `RUN` steps; they do not configure Docker Engine or the Buildx client's base-image/token traffic. See [Network and remote access](Network_and_Remote_Access.md#proxies-and-mirrors).

### Legacy fallback

If the Buildx command fails, the legacy builder remains a compatibility fallback:

```bash
DOCKER_BUILDKIT=0 docker build -t "$IMAGE" .
```

Diagnose the failing Buildx stage rather than changing TLS or authentication semantics.

## 6. Tag and push

If the local build used a different tag, add the full Harbor reference and push it explicitly:

```bash
docker tag <local-image>:<local-tag> \
  harbor.cvgl.lab/<project>/<image>:<version-tag>
docker push harbor.cvgl.lab/<project>/<image>:<version-tag>
```

Use a new, meaningful version tag for changed content, confirm project authorization, and record the resulting digest.

## 7. Use the image with Determined

Reference the pushed tag or pinned digest in the task configuration:

```yaml
environment:
  image: harbor.cvgl.lab/<project>/<image>:<version-tag>
```

See the [Determined compute guide](Determined_AI_User_Guide.md) and [MCP workflow](Agent_Workflow.md) for planning and submission. Follow [Shared storage](Shared_Storage.md) for code, datasets, checkpoints, and outputs. The image should contain the runtime environment; changing data and run artifacts belong on shared storage.

## Troubleshooting

- A default Buildx build reports `x509: certificate signed by unknown authority` while requesting `https://harbor.cvgl.lab/service/token`: run that Buildx command with the documented `SSL_CERT_DIR`.
- `unauthorized` or `denied`: run `docker login` again and confirm access to the Harbor project. This is an authorization failure, not a CA failure.
- A builder reports DNS lookup failure or an isolated BuildKit registry error: use the three-layer diagnosis in [Buildx and Harbor](Buildx_and_Harbor.md#failure-stages).
- A package constraint creates a file such as `=0.16.0`: quote the complete requirement passed to the shell.
- A Determined task cannot see code or output: check its bind mounts and use an approved shared-storage root.
