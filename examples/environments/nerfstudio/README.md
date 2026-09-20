[English](README.md) | [简体中文](README.zh.md)

# Nerfstudio Dockerfile

This older recipe contains pinned and mutable upstream dependencies. Review and
update them before use. The top-level [`examples/environments` index](../README.md)
explains the assumptions shared by all examples.

## Build with Makefile

The Makefile contains the target image, tag, proxy build arguments, and a
retained `DOCKER_BUILDKIT=0` fallback. For direct Buildx builds, use the
[current login-node setup](../../../docs/Buildx_and_Harbor.md). `MAX_JOBS` is a build
argument used by PyTorch C++/CUDA extension builds; it does not persist in the
final runtime image. Override its default with, for example,
`make build_nerf MAX_JOBS=8`.

### Build the image only

The default `make` target builds both images without pushing. To build only the
Nerfstudio stage:

``` bash
make build_nerf
```

### Build and push the image to Harbor

``` bash
make push_nerf
```
