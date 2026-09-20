[English](README.md) | [简体中文](README.zh.md)

<a id="container-environment-examples"></a>
# 容器环境示例

这些目录保留了早期项目使用过的环境配方。它们是供审查的起点，不是当前受支持
镜像的目录。基础镜像、操作系统仓库、源码分支、package index 和上游项目自编写
这些配方以来可能已经发生变化。使用前必须验证当前的构建和运行兼容性。

| 示例 | 原始用途 | 重要假设 |
| --- | --- | --- |
| [`determined-tmux`](determined-tmux/) | 在旧版 Determined 环境中添加 `tmux` | 历史 CUDA 11.3 / PyTorch 1.10 / Determined 0.19.4 基础镜像 |
| [`dreambooth`](dreambooth/) | DreamBooth 和 Stable Diffusion 研究环境 | 历史 NGC 22.12 基础镜像；构建时会 clone 多个源码仓库 |
| [`lietorch-opencv`](lietorch-opencv/) | OpenCV 4.6 和针对 SM 8.6 修补的 lietorch build | 镜像会复制随附的 [`.condarc`](lietorch-opencv/.condarc)；配方针对旧版 Python/CUDA stack |
| [`nerf-env`](nerf-env/README.zh.md) | 通用 NeRF/BAD-NeRF 环境 | 历史 NGC PyTorch 23.01 基础镜像；其 README 记录了原始 RTX 4090 目标 |
| [`nerfstudio`](nerfstudio/README.zh.md) | 多阶段 Nerfstudio/COLMAP/OpenCV 环境 | CUDA 11.8 和 PyTorch 2.1.2 时代的配方；仍包含需要审查的可变上游分支 |

使用示例之前：

1. 阅读完整 Dockerfile 以及所有 helper script 或 Makefile。
2. 用审查过的 commit、版本和 image digest 替换可变分支及浮动依赖。
3. 确认 CUDA architecture、framework ABI、Python 版本和目标 GPU。
4. 检查每个外部 URL 和 package name，不要假定旧 mirror 或 repository 仍然存在。
5. 使用[自定义容器操作指南](../../docs/Custom_Containerized_Environment.zh.md)中当前与
   Harbor 兼容的路径构建：

   ```bash
   DOCKER_BUILDKIT=0 docker build -t <local-image>:<test-tag> .
   ```

6. 先在本地测试且不要推送；镜像通过审查后，再使用新的 release tag，并记录
   Harbor digest。

Nerfstudio Makefile 包含显式 push target。调用任何 `push_*` target 之前，请检查
registry、project、tag、proxy 和 build argument。任务规划和共享数据放置请参阅
[Determined compute 指南](../../docs/Determined_AI_User_Guide.zh.md)、
[MCP 工作流](../../docs/Agent_Workflow.zh.md)和
[共享存储指南](../../docs/Shared_Storage.zh.md)。
