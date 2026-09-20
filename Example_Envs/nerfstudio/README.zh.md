[English](README.md) | [简体中文](README.zh.md)

<a id="historical-nerfstudio-dockerfile"></a>
# 历史 Nerfstudio Dockerfile

这个配方是当前兼容性尚未验证的历史参考。使用前请审查其中固定和可变的上游
依赖。顶层 [`Example_Envs` 索引](../README.zh.md)说明了所有示例的状态。

<a id="build-with-makefile"></a>
## 使用 Makefile 构建

Makefile 包含目标 image、tag、proxy build argument，以及当前
`DOCKER_BUILDKIT=0` 兼容设置。`MAX_JOBS` 是 PyTorch C++/CUDA extension build
使用的 build argument；它不会保留在最终 runtime image 中。例如可用
`make build_nerf MAX_JOBS=8` 覆盖默认值。

<a id="build-the-image-only"></a>
### 只构建镜像

默认 `make` target 会构建两个镜像但不会推送。只构建 Nerfstudio stage：

``` bash
make build_nerf
```

<a id="build-and-push-the-image-to-harbor"></a>
### 构建镜像并推送到 Harbor

``` bash
make push_nerf
```
