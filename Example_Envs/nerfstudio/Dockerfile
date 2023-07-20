FROM nvcr.io/nvidia/cuda:11.8.0-devel-ubuntu22.04 AS base

ARG MAX_JOBS 32
ARG DEBIAN_FRONTEND=noninteractive
ARG CUDA_ARCHITECTURES=89;86
ENV TORCH_CUDA_ARCH_LIST="8.9;8.6" TORCH_NVCC_FLAGS="-Xfatbin -compress-all"
ENV TCNN_CUDA_ARCHITECTURES=${CUDA_ARCHITECTURES}
ENV TZ=Asia/Shanghai LANG=C.UTF-8 LC_ALL=C.UTF-8 PIP_NO_CACHE_DIR=1 PIP_CACHE_DIR=/tmp/

RUN sed -i "s/archive.ubuntu.com/mirrors.ustc.edu.cn/g" /etc/apt/sources.list &&\
    sed -i "s/security.ubuntu.com/mirrors.ustc.edu.cn/g" /etc/apt/sources.list &&\
    rm -f /etc/apt/sources.list.d/* &&\
    rm -rf /opt/hpcx/ &&\
    apt-get update && apt-get upgrade -y &&\
    apt-get install -y --no-install-recommends \
        # Determined requirements and common tools
        autoconf automake autotools-dev build-essential ca-certificates \
        make cmake ninja-build pkg-config g++ ccache yasm \
        ccache doxygen graphviz plantuml \
        daemontools krb5-user ibverbs-providers libibverbs1 \
        libkrb5-dev librdmacm1 libssl-dev libtool \
        libnuma1 libnuma-dev libpmi2-0-dev \
        openssh-server openssh-client pkg-config nfs-common \
        ## Tools
        git curl wget unzip nano vim-tiny net-tools sudo htop iotop \
        cloc rsync screen tmux xz-utils software-properties-common \
        ## Deps
        ffmpeg \
        libatlas-base-dev \
        libboost-filesystem-dev \
        libboost-graph-dev \
        libboost-program-options-dev \
        libboost-system-dev \
        libboost-test-dev \
        libcereal-dev \
        libcgal-dev \
        libeigen3-dev \
        libflann-dev \
        libfreeimage-dev \
        libgflags-dev \
        libglew-dev \
        libgoogle-glog-dev \
        libhdf5-dev \
        libmetis-dev \
        libprotobuf-dev \
        libqt5opengl5-dev \
        libsqlite3-dev \
        libsuitesparse-dev \
        protobuf-compiler \
        python-is-python3 \
        python3.10-dev \
        python3-pip \
        qtbase5-dev \
    && rm /etc/ssh/ssh_host_ecdsa_key \
    && rm /etc/ssh/ssh_host_ed25519_key \
    && rm /etc/ssh/ssh_host_rsa_key \
    && cp /etc/ssh/sshd_config /etc/ssh/sshd_config_bak \
    && sed -i "s/^.*X11Forwarding.*$/X11Forwarding yes/" /etc/ssh/sshd_config \
    && sed -i "s/^.*X11UseLocalhost.*$/X11UseLocalhost no/" /etc/ssh/sshd_config \
    && grep "^X11UseLocalhost" /etc/ssh/sshd_config || echo "X11UseLocalhost no" >> /etc/ssh/sshd_config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Install GLOG (required by ceres).
RUN git clone --branch v0.6.0 https://github.com/google/glog --single-branch &&\
    cd glog &&\
    mkdir build &&\
    cd build &&\
    cmake .. &&\
    make -j `nproc` &&\
    make install &&\
    rm -rf /tmp/*
# Add glog path to LD_LIBRARY_PATH.
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib"

# Install Ceres-solver (required by colmap).
RUN git clone --branch 2.1.0 https://ceres-solver.googlesource.com/ceres-solver --single-branch &&\
    cd ceres-solver &&\
    git checkout $(git describe --tags) &&\
    mkdir build &&\
    cd build &&\
    cmake .. -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF &&\
    make -j `nproc` &&\
    make install &&\
    rm -rf /tmp/*

# Install colmap.
RUN git clone --branch 3.8 https://github.com/colmap/colmap --single-branch &&\
    cd colmap &&\
    mkdir build &&\
    cd build &&\
    cmake .. -DCUDA_ENABLED=ON \
             -DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCHITECTURES} &&\
    make -j `nproc` &&\
    make install &&\
    rm -rf /tmp/*

# Install Determined AI and python deps
ENV PYTHONUNBUFFERED=1 PYTHONFAULTHANDLER=1 PYTHONHASHSEED=0
ENV JUPYTER_CONFIG_DIR=/run/determined/jupyter/config
ENV JUPYTER_DATA_DIR=/run/determined/jupyter/data
ENV JUPYTER_RUNTIME_DIR=/run/determined/jupyter/runtime
RUN git clone https://github.com/LingzheZhao/determinedai-container-scripts &&\
    cd determinedai-container-scripts &&\
    git checkout v0.1 &&\
    pip config set global.index-url https://mirrors.bfsu.edu.cn/pypi/web/simple &&\
    pip install -U pip setuptools pathtools promise pybind11 &&\
    pip install determined && pip uninstall -y determined &&\
    pip install -r notebook-requirements.txt &&\
    ./add_det_nobody_user.sh &&\
    ./install_libnss_determined.sh &&\
    rm -rf /tmp/*

# Install pycolmap, required by hloc.
RUN git clone --branch v0.4.0 --recursive https://github.com/colmap/pycolmap &&\
    cd pycolmap &&\
    pip install . &&\
    rm -rf /tmp/*

# Install pyceres from source
RUN git clone --branch v1.0 --recursive https://github.com/cvg/pyceres &&\
    cd pyceres &&\
    pip install -e . &&\
    rm -rf /tmp/*


FROM base AS nerfstudio
RUN pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118 &&\
    pip install git+https://github.com/cvg/Hierarchical-Localization@master &&\
    pip install git+https://github.com/cvg/pixel-perfect-sfm@main &&\
    pip install git+https://github.com/NVlabs/tiny-cuda-nn@master#subdirectory=bindings/torch &&\
    rm -rf /tmp/*

RUN pip install open3d>=0.16.0 --ignore-installed &&\
    # Stable version
    pip install "nerfstudio[dev,doc]" -i https://pypi.org/simple/ &&\
    # Nightly version
    pip install git+https://github.com/nerfstudio-project/nerfstudio@main -i https://pypi.org/simple/ &&\
    pip install coverage einops torchtyping>=0.1.4 kplanes-nerfstudio &&\
    rm -rf /tmp/*

CMD ns-install-cli --mode install && /bin/bash


FROM base AS sdfstudio
ARG NERF_ACC_VER=0.3.5
RUN git clone --recursive https://github.com/pytorch/pytorch &&\
    cd pytorch &&\
    git checkout 44dac51 &&\
    git submodule sync &&\
    git submodule update --init --recursive --jobs 0 &&\
    python setup.py install &&\
    rm -rf /tmp/*

RUN git clone --branch v0.14.1 https://github.com/pytorch/vision torchvision --single-branch &&\
    cd torchvision &&\
    python setup.py install &&\
    rm -rf /tmp/*

COPY sdfstudio/requirements.txt /tmp/requirements.txt
RUN pip install git+https://github.com/cvg/Hierarchical-Localization@master &&\
    pip install git+https://github.com/NVlabs/tiny-cuda-nn@master#subdirectory=bindings/torch &&\
    pip install open3d>=0.16.0 --ignore-installed &&\
    pip install lpips --no-deps &&\
    pip install -r /tmp/requirements.txt &&\
    rm -rf /tmp/*

RUN cd /tmp &&\
    wget https://github.com/KAIR-BAIR/nerfacc/archive/refs/tags/v${NERF_ACC_VER}.tar.gz &&\
    tar xvzf v${NERF_ACC_VER}.tar.gz &&\
    cd nerfacc-${NERF_ACC_VER} &&\
    python setup.py install &&\
    rm -rf /tmp/*

COPY sdfstudio/pyproject.toml /tmp
RUN cd /tmp &&\
    git clone https://github.com/autonomousvision/sdfstudio &&\
    cd sdfstudio &&\
    rm pyproject.toml &&\
    cp /tmp/pyproject.toml . &&\
    pip install . &&\
    rm -rf /tmp/*

CMD ns-install-cli --mode install && /bin/bash
