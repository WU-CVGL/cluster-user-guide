# Trying to run this container with Vulkan support but failed
# with CUDA 11.8 + RTX 4090, may due to problems with upstream CUDA & drivers
# Checkout https://gitlab.com/nvidia/container-images/vulkan

docker run -it \
--name nerf-slam-cuda-11-8 \
--gpus='all,"capabilities=compute,utility,graphics,display"' \
--ipc=host \
-v $XDG_RUNTIME_DIR:$XDG_RUNTIME_DIR \
-v ${XAUTHORITY}:${XAUTHORITY} \
-v /tmp/.X11-unix:/tmp/.X11-unix \
-e DISPLAY=$DISPLAY \
-e NVIDIA_VISIBLE_DEVICES=all \
-e NVIDIA_DRIVER_CAPABILITIES=all \
-e NVIDIA_DISABLE_REQUIRE=1 \
--device /dev/dri \
-v /etc/vulkan/icd.d/nvidia_icd.json:/etc/vulkan/icd.d/nvidia_icd.json \
-v /etc/vulkan/implicit_layer.d/nvidia_layers.json:/etc/vulkan/implicit_layer.d/nvidia_layers.json \
-v /usr/share/glvnd/egl_vendor.d/10_nvidia.json:/usr/share/glvnd/egl_vendor.d/10_nvidia.json \
-v /mnt/sda1:/mnt/sda1 \
-v /mnt/sdb1:/mnt/sdb1 \
harbor.cvgl.lab/library/zlz-taichi-nerf-slam:22.12
