[English](README.md) | [简体中文](README.zh.md)

# Historical Nerfstudio Dockerfile

This recipe is a historical reference with unverified current compatibility.
Review its pinned and mutable upstream dependencies before use. The top-level
[`Example_Envs` index](../README.md) explains the status of all examples.

## Build with Makefile

The Makefile contains the target image, tag, proxy build arguments, and the
current `DOCKER_BUILDKIT=0` compatibility setting. `MAX_JOBS` is a build
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
