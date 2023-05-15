NERF_NAME=harbor.cvgl.lab/library/zlz-nerfstudio
SDF_NAME=harbor.cvgl.lab/library/zlz-sdfstudio
BASE_VERSION=cuda-11.8-devel-ubuntu22.04-torch-1.14.0a0_44dac51-230515
PREBUILT_VERSION=22.12

build: build_from_scratch build_from_prebuilt

# Build pytorch, torchvision, nerfacc
build_from_scratch: build_from_scratch_nerf build_from_scratch_sdf

build_from_scratch_base:
	docker build -t base -f Dockerfile.base .

build_from_scratch_nerf: build_from_scratch_base
	docker build -t $(NERF_NAME):$(BASE_VERSION) -f Dockerfile.nerfstudio .

build_from_scratch_sdf: build_from_scratch_base
	docker build -t $(SDF_NAME):$(BASE_VERSION) -f Dockerfile.sdfstudio .

# Use prebuilt pytorch, torchvision (from torchngp env) and nerfacc
build_from_prebuilt: build_from_prebuilt_nerf build_from_prebuilt_sdf

build_from_prebuilt_nerf:
	docker build -t ${NERF_NAME}:${PREBUILT_VERSION} -f Dockerfile.torchngp-nerf .

build_from_prebuilt_sdf:
	docker build -t ${SDF_NAME}:${PREBUILT_VERSION} -f Dockerfile.torchngp-sdf .