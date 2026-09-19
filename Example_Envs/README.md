# Container environment examples

These directories preserve environment recipes used by earlier projects. They
are starting points for review, not a catalog of currently supported images.
Base images, OS repositories, source branches, package indexes, and upstream
projects may have changed since each recipe was written. Current build and
runtime compatibility must be verified before use.

| Example | Intended use | Important assumptions |
| --- | --- | --- |
| [`determined-tmux`](./determined-tmux/) | Adds `tmux` to an older Determined environment | Historical CUDA 11.3 / PyTorch 1.10 / Determined 0.19.4 base |
| [`dreambooth`](./dreambooth/) | DreamBooth and Stable Diffusion research environment | Historical NGC 22.12 base; several source repositories are cloned during the build |
| [`lietorch-opencv`](./lietorch-opencv/) | OpenCV 4.6 and a patched lietorch build for SM 8.6 | The included [`.condarc`](./lietorch-opencv/.condarc) is copied into the image; the recipe targets an older Python/CUDA stack |
| [`nerf-env`](./nerf-env/) | General NeRF/BAD-NeRF environment | Historical NGC PyTorch 23.01 base; its README records the original RTX 4090 intent |
| [`nerfstudio`](./nerfstudio/) | Multi-stage Nerfstudio/COLMAP/OpenCV environment | CUDA 11.8 and PyTorch 2.1.2-era recipe; mutable upstream branches remain and require review |

Before using an example:

1. Read the complete Dockerfile and any helper script or Makefile.
2. Replace mutable branches and floating dependencies with reviewed commits,
   versions, and image digests.
3. Confirm the CUDA architecture, framework ABI, Python version, and target GPU.
4. Check every external URL and package name without assuming an old mirror or
   repository still exists.
5. Build with the current Harbor-compatible path described in the
   [custom-container HOWTO](../Custom_Containerized_Environment.md):

   ```bash
   DOCKER_BUILDKIT=0 docker build -t <local-image>:<test-tag> .
   ```

6. Test locally without pushing, then use a new release tag and record the
   Harbor digest if the image is approved.

The Nerfstudio Makefile has explicit push targets. Review its registry,
project, tag, proxy, and build arguments before invoking any `push_*` target.
For task planning and shared data placement, see the
[Determined compute guide](../Determined_AI_User_Guide.md),
[MCP workflow](../Agent_Workflow.md), and
[shared-storage guide](../Shared_Storage.md).
