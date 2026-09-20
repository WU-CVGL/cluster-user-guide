[English](README.md) | [简体中文](README.zh.md)

# Container environment examples

These directories contain older environment recipes. They are starting points,
not a catalog of supported images. Review and update their base images, OS
repositories, source branches, package indexes, and upstream dependencies
before use.

| Example | Intended use | Important assumptions |
| --- | --- | --- |
| [`determined-tmux`](determined-tmux/) | Adds `tmux` to an older Determined environment | CUDA 11.3 / PyTorch 1.10 / Determined 0.19.4 base |
| [`dreambooth`](dreambooth/) | DreamBooth and Stable Diffusion research environment | NGC 22.12 base; several source repositories are cloned during the build |
| [`lietorch-opencv`](lietorch-opencv/) | OpenCV 4.6 and a patched lietorch build for SM 8.6 | The included [`.condarc`](lietorch-opencv/.condarc) is copied into the image; the recipe targets an older Python/CUDA stack |
| [`nerf-env`](nerf-env/) | General NeRF/BAD-NeRF environment | NGC PyTorch 23.01 base; targets RTX 4090 |
| [`nerfstudio`](nerfstudio/) | Multi-stage Nerfstudio/COLMAP/OpenCV environment | CUDA 11.8 and PyTorch 2.1.2-era recipe; mutable upstream branches remain and require review |

Before using an example:

1. Read the complete Dockerfile and any helper script or Makefile.
2. Replace mutable branches and floating dependencies with reviewed commits,
   versions, and image digests.
3. Confirm the CUDA architecture, framework ABI, Python version, and target GPU.
4. Check every external URL and package name without assuming an old mirror or
   repository still exists.
5. On the login node, use the current Buildx path described in the
   [custom-container HOWTO](../../docs/Custom_Containerized_Environment.md):

   ```bash
   SSL_CERT_DIR=/etc/docker/certs.d/harbor.cvgl.lab \
     docker buildx build --builder default --load -t <local-image>:<test-tag> .
   ```

6. Build and run locally without pushing. After review, use a new release tag
   and record the Harbor digest.

Some build helpers use `DOCKER_BUILDKIT=0` as a compatibility fallback. A
working Buildx transport does not guarantee that an older recipe's dependencies
still resolve.
The Nerfstudio Makefile has explicit push targets. Review its registry,
project, tag, proxy, and build arguments before invoking any `push_*` target.
For task planning and shared data placement, see the
[Determined compute guide](../../docs/Determined_AI_User_Guide.md),
[MCP workflow](../../docs/Agent_Workflow.md), and
[shared-storage guide](../../docs/Shared_Storage.md).
