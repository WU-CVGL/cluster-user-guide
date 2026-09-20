[English](Custom_Containerized_Environment.md) | [简体中文](Custom_Containerized_Environment.zh.md)

# Build and use a custom container image

This HOWTO covers the current CVGL Harbor workflow. It assumes that Docker is
already installed and that you are allowed to build images on the selected
machine. On managed hosts, ask an administrator before changing Docker trust or
restarting the Docker service.

The files under [`Example_Envs`](./Example_Envs/README.md) are historical
references. Review and pin every dependency before using one; an example's
presence does not mean that its image currently builds or runs.

## 1. Choose and pin a base image

Prefer an administrator-approved image mirrored in `harbor.cvgl.lab`. Use a
versioned tag, and use a digest when reproducibility matters:

```dockerfile
FROM harbor.cvgl.lab/<project>/<base-image>:<version-tag>
# Stronger reproducibility after the digest has been verified:
# FROM harbor.cvgl.lab/<project>/<base-image>@sha256:<digest>
```

Avoid floating tags such as `latest`. A tag can be moved; a digest identifies
the exact manifest that was reviewed.

The historical RTX 4090 recipes here use CUDA 11.8-or-newer bases. Compatibility also depends on
the framework, driver, compiler, and any CUDA extensions, so CUDA version alone
is not a complete compatibility check.

## 2. Trust the Harbor CA

Obtain the Harbor CA certificate and its SHA-256 fingerprint through a trusted,
authenticated channel, such as directly from the system administrator. Do not
bootstrap trust by downloading a certificate with TLS verification disabled and
then trusting it without an out-of-band fingerprint check.

Inspect the certificate before installation:

```bash
openssl x509 -in harbor-ca.crt -noout -subject -issuer -dates -fingerprint -sha256
```

Compare that fingerprint with the administrator-published value. On a Linux
Docker Engine host that you administer, install the verified CA as a `.crt`
file under the directory named exactly after the registry:

```bash
sudo install -d -m 0755 /etc/docker/certs.d/harbor.cvgl.lab
sudo install -m 0644 harbor-ca.crt /etc/docker/certs.d/harbor.cvgl.lab/ca.crt
sudo systemctl restart docker
```

On a managed cluster host, do not overwrite an existing certificate or restart
Docker yourself; ask the administrator to verify or repair the trust setup.
Docker treats every `*.crt` file in that directory as a CA root. An existing
administrator-provided name such as `server.crt` is also valid if the file is
the verified CA certificate. Docker Desktop and rootless Docker use different
certificate locations; follow the
[Docker registry certificate documentation](https://docs.docker.com/engine/security/certificates/)
for that installation.

An HTTP `401 Unauthorized` response from this read-only probe is expected when
TLS trust works but no Harbor credentials were supplied:

```bash
curl --silent --show-error --output /dev/null --write-out '%{http_code}\n' \
  --cacert harbor-ca.crt https://harbor.cvgl.lab/v2/
```

## 3. Log in without exposing the password

For interactive use, let Docker prompt for the password:

```bash
docker login harbor.cvgl.lab --username <username>
```

For controlled automation, pass a secret through standard input. Do not use
`docker login -p ...`, because the password becomes a command-line argument:

```bash
printf '%s' "$HARBOR_PASSWORD" |
  docker login harbor.cvgl.lab --username <username> --password-stdin
```

Docker may store the resulting credential in `~/.docker/config.json`; configure
a Docker credential store where available. See
[`docker login`](https://docs.docker.com/reference/cli/docker/login/) for the
credential-store and `--password-stdin` behavior.

## 4. Write the Dockerfile

Keep the build context small and use a `.dockerignore`. A minimal extension of
an approved base looks like this:

```dockerfile
FROM harbor.cvgl.lab/<project>/<base-image>:<version-tag>

ARG DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PIP_NO_CACHE_DIR=1

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --requirement /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt
```

Pin Python packages and source checkouts. Quote shell requirements that contain
operators, for example `python -m pip install "nerfstudio>=1.0"`, so `>` is not
interpreted as shell redirection. Do not pass tokens or passwords as build
arguments: build arguments and layers are not a secret store.

## 5. Build with the current compatible path

For the current CVGL Harbor deployment with its self-signed CA, the supported
compatibility path is the legacy Docker builder:

```bash
IMAGE=harbor.cvgl.lab/<project>/<image>:<version-tag>
DOCKER_BUILDKIT=0 docker build -t "$IMAGE" .
```

Keep `DOCKER_BUILDKIT=0` for this path. The trailing `.` is the build context.
If the build itself needs the site proxy, use the administrator-provided proxy
URL and pass only non-secret proxy addresses:

```bash
DOCKER_BUILDKIT=0 docker build \
  --build-arg http_proxy=<proxy-url> \
  --build-arg https_proxy=<proxy-url> \
  -t "$IMAGE" .
```

If the Docker daemon needs a proxy to pull the base image, ask the administrator
to configure it. A build argument configures `RUN` steps in the temporary build
container; it does not configure the Docker daemon.

### Optional, unverified BuildKit migration

BuildKit has not been validated against this Harbor deployment. Do not replace
the compatible command above yet. A future migration should use a separate
`docker-container` builder with an explicit registry CA; do not apply a
`--buildkitd-config` procedure to the existing default `docker` driver.

Example configuration for a dedicated test builder:

```toml
# /absolute/path/to/cvgl-buildkitd.toml
[registry."harbor.cvgl.lab"]
  ca = ["/absolute/path/to/verified-harbor-ca.crt"]
```

On a machine where you can run test builds, create and inspect the isolated
builder, then run a non-pushing test build:

```bash
docker buildx create \
  --name cvgl-harbor-test \
  --driver docker-container \
  --buildkitd-config /absolute/path/to/cvgl-buildkitd.toml \
  --bootstrap

docker buildx inspect cvgl-harbor-test
docker buildx build --builder cvgl-harbor-test --load -t "$IMAGE" .
```

Docker documents how the CA is copied into a `docker-container` builder in
[Configure BuildKit](https://docs.docker.com/build/buildkit/configure/). Treat
this as a migration experiment until pulling the base image and a complete
non-pushing build have both been verified.

## 6. Tag and push

If the local build used a different tag, add the full Harbor reference and push
it explicitly:

```bash
docker tag <local-image>:<local-tag> \
  harbor.cvgl.lab/<project>/<image>:<version-tag>
docker push harbor.cvgl.lab/<project>/<image>:<version-tag>
```

Use a new, meaningful version tag for changed content. Record the digest printed
by `docker push` or shown by Harbor. Keep release tags stable rather than
overwriting them; use the recorded digest for reproducible jobs.

## 7. Use the image with Determined

Reference the pushed tag or verified digest in the task configuration:

```yaml
environment:
  image: harbor.cvgl.lab/<project>/<image>:<version-tag>
```

See the [Determined compute guide](./Determined_AI_User_Guide.md) and the
[MCP workflow](./Agent_Workflow.md) for task planning and submission. Follow the
[shared-storage guide](./Shared_Storage.md) for code, datasets, checkpoints, and
outputs. The image should hold the runtime environment; changing datasets and
run artifacts belong on shared storage.

## Troubleshooting

- `x509: certificate signed by unknown authority`: verify the CA fingerprint,
  certificate filename extension, registry directory name, and the certificate
  location for your Docker installation. Do not use an insecure-registry flag.
- `unauthorized` or `denied`: log in again and confirm access to the Harbor
  project. TLS trust and registry authorization are separate checks.
- A BuildKit pull fails while the compatible build works: continue with
  `DOCKER_BUILDKIT=0`; the isolated BuildKit CA path remains unverified.
- A package constraint creates a file such as `=0.16.0`: quote the complete
  requirement passed to the shell.
- A job cannot see code or output: check the Determined bind mounts and place
  the workload under an approved shared-storage root.
