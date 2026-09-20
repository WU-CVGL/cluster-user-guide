[English](README.md) | [简体中文](README.zh.md)

<a id="container-environment-examples"></a>
# 容器环境示例

这些目录包含较早的环境配方。它们是起点，不是受支持镜像的目录。使用前应审查并
更新其中的基础镜像、操作系统仓库、源码分支、package index 和上游依赖。

| 示例 | 原始用途 | 重要假设 |
| --- | --- | --- |
| [`determined-tmux`](determined-tmux/) | 在旧版 Determined 环境中添加 `tmux` | CUDA 11.3 / PyTorch 1.10 / Determined 0.19.4 基础镜像 |
| [`dreambooth`](dreambooth/) | DreamBooth 和 Stable Diffusion 研究环境 | NGC 22.12 基础镜像；构建时会 clone 多个源码仓库 |
| [`lietorch-opencv`](lietorch-opencv/) | OpenCV 4.6 和针对 SM 8.6 修补的 lietorch build | 镜像会复制随附的 [`.condarc`](lietorch-opencv/.condarc)；配方针对旧版 Python/CUDA stack |
| [`nerf-env`](nerf-env/README.zh.md) | 通用 NeRF/BAD-NeRF 环境 | NGC PyTorch 23.01 基础镜像；目标为 RTX 4090 |
| [`nerfstudio`](nerfstudio/README.zh.md) | 多阶段 Nerfstudio/COLMAP/OpenCV 环境 | CUDA 11.8 和 PyTorch 2.1.2 时代的配方；仍包含需要审查的可变上游分支 |

使用示例之前：

1. 阅读完整 Dockerfile 以及所有 helper script 或 Makefile。
2. 用审查过的 commit、版本和 image digest 替换可变分支及浮动依赖。
3. 确认 CUDA architecture、framework ABI、Python 版本和目标 GPU。
4. 检查每个外部 URL 和 package name，不要假定旧 mirror 或 repository 仍然存在。
5. 在登录节点上，使用[自定义容器操作指南](../../docs/Custom_Containerized_Environment.zh.md)中
   当前的 Buildx 方式构建：

   ```bash
   SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
     docker buildx build --builder default --load -t <local-image>:<test-tag> .
   ```

6. 先在本地构建并运行，不要推送。审查后使用新的 release tag，并记录 Harbor
   digest。

部分构建脚本使用 `DOCKER_BUILDKIT=0` 作为兼容回退。Buildx 访问链路可用不代表
旧配方中的依赖仍然能够解析。
Nerfstudio Makefile 包含显式 push target。调用任何 `push_*` target 之前，请检查
registry、project、tag、proxy 和 build argument。任务规划和共享数据放置请参阅
[Determined compute 指南](../../docs/Determined_AI_User_Guide.zh.md)、
[MCP 工作流](../../docs/Agent_Workflow.zh.md)和
[共享存储指南](../../docs/Shared_Storage.zh.md)。
