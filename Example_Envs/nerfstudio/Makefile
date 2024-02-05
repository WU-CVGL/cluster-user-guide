NERF_NAME=harbor.cvgl.lab/library/zlz-nerfstudio
NERF_VERSION=v1.0.1-cu118-ubuntu2204-torch2.1.2-240205
NERF=$(NERF_NAME):$(NERF_VERSION)

SDF_NAME=harbor.cvgl.lab/library/zlz-sdfstudio
SDF_VERSION=nightly-cu118-ubuntu2204-torch1.14.0a0_44dac51-230720
SDF=$(SDF_NAME):$(SDF_VERSION)

MY_HTTP_PROXY=http://10.0.1.68:8889
BUILD_ARGS=--build-arg http_proxy=$(MY_HTTP_PROXY) --build-arg https_proxy=$(MY_HTTP_PROXY)

build: push_nerf push_sdf

build_nerf:
	docker build -t $(NERF) --target nerfstudio $(BUILD_ARGS) .

push_nerf: build_nerf
	docker push $(NERF)

build_sdf:
	docker build -t $(SDF) --target sdfstudio $(BUILD_ARGS) .

push_sdf: build_sdf
	docker push $(SDF)
