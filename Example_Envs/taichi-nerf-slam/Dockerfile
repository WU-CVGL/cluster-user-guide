FROM nvcr.io/nvidia/pytorch:22.12-py3
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai LANG=C.UTF-8 LC_ALL=C.UTF-8 PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1 PYTHONFAULTHANDLER=1 PYTHONHASHSEED=0 TORCH_CUDA_ARCH_LIST="8.6;8.9" MESA_GL_VERSION_OVERRIDE="3.3" XDG_RUNTIME_DIR=/tmp
ENV PATH="${PATH}:/opt/hpcx/ompi/bin"
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/hpcx/ompi/lib"
ARG CMAKE_VERSION=3.26.3
ARG OPENEXR_VERSION=3.1.7
ARG OPENCV_VERSION=4.7.0
ARG CLANG_VER=12
ARG MAX_JOBS=16

RUN sed -i "s/archive.ubuntu.com/mirrors.ustc.edu.cn/g" /etc/apt/sources.list &&\
    sed -i "s/security.ubuntu.com/mirrors.ustc.edu.cn/g" /etc/apt/sources.list &&\
    rm -f /etc/apt/sources.list.d/* &&\
    apt-get update && apt-get upgrade -y &&\
    apt-get install -y --no-install-recommends \
        autoconf automake autotools-dev build-essential ca-certificates software-properties-common \
        make ninja-build yasm pkg-config checkinstall ccache doxygen gdb \
        gcc gcc-multilib g++ g++-multilib gfortran \
        git nano curl wget unzip p7zip-full xz-utils zstd \
        daemontools net-tools cloc htop iftop iotop rsync \
        libatlas-base-dev libboost-all-dev libcereal-dev libcgal-dev \
        libcxsparse3 libeigen3-dev liblapack-dev liblapacke-dev \
        metis libmetis-dev libopenblas-dev libsuitesparse-dev \
        libgtk2.0-dev libgtk-3-dev libglew-dev libgl1-mesa-dev libgl1-mesa-glx mesa-utils \
        libgflags-dev libgoogle-glog-dev libgtest-dev libprotobuf-dev protobuf-compiler \
        libgphoto2-dev libhdf5-dev libjpeg-dev libpng-dev libtiff-dev libtiff-dev \
        libavcodec-dev libavformat-dev libavutil-dev libavdevice-dev libavresample-dev \
        libpostproc-dev libpq-dev libswscale-dev \
        libtbb2 libtbb-dev libxine2-dev zlib1g-dev \
        krb5-user libkrb5-dev libssl-dev libtool libyaml-dev libyaml-cpp-dev \
        ibverbs-providers libibverbs1 librdmacm1 \
        libnuma1 libnuma-dev libpmi2-0-dev \
        libxvidcore-dev x264 libx264-dev libfaac-dev libmp3lame-dev libtheora-dev \
        libfaac-dev libmp3lame-dev libvorbis-dev \
        libopencore-amrnb-dev libopencore-amrwb-dev \
        libv4l-dev v4l-utils \
        libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
        openssh-server openssh-client nfs-common\
        colmap ffmpeg \
        # dev
        gcc-10 gcc-10-multilib g++-10 g++-10-multilib cpp-10 \
        qt5-default \
        libllvm-${CLANG_VER}-ocaml-dev libllvm${CLANG_VER} llvm-${CLANG_VER} \
        llvm-${CLANG_VER}-dev llvm-${CLANG_VER}-doc llvm-${CLANG_VER}-examples \
        llvm-${CLANG_VER}-runtime \
        clang-${CLANG_VER} clang-tools-${CLANG_VER} clang-${CLANG_VER}-doc \
        libclang-common-${CLANG_VER}-dev libclang-${CLANG_VER}-dev \
        libclang1-${CLANG_VER} \
        clang-format-${CLANG_VER} python3-clang-${CLANG_VER} \
        clangd-${CLANG_VER} clang-tidy-${CLANG_VER} \
        libfuzzer-${CLANG_VER}-dev lldb-${CLANG_VER} lld-${CLANG_VER} \
        libc++-${CLANG_VER}-dev libc++abi-${CLANG_VER}-dev \
        libomp-${CLANG_VER}-dev libclc-${CLANG_VER}-dev \
    # Configure clang, gcc, ssh
    && update-alternatives \
            --install /usr/bin/gcc gcc /usr/bin/gcc-10 100 \
            --slave /usr/bin/g++ g++ /usr/bin/g++-10 \
            --slave /usr/bin/gcov gcov /usr/bin/gcov-10 \
    # && update-alternatives --install /usr/bin/cc cc /usr/bin/clang 100 \
    # && update-alternatives --install /usr/bin/c++ c++ /usr/bin/clang++ 100 \
    && apt-get purge -y unattended-upgrades \
    && rm /etc/ssh/ssh_host_ecdsa_key \
    && rm /etc/ssh/ssh_host_ed25519_key \
    && rm /etc/ssh/ssh_host_rsa_key \
    && cp /etc/ssh/sshd_config /etc/ssh/sshd_config_bak \
    && sed -i "s/^.*X11Forwarding.*$/X11Forwarding yes/" /etc/ssh/sshd_config \
    && sed -i "s/^.*X11UseLocalhost.*$/X11UseLocalhost no/" /etc/ssh/sshd_config \
    && grep "^X11UseLocalhost" /etc/ssh/sshd_config || echo "X11UseLocalhost no" >> /etc/ssh/sshd_config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install TBB & Determined AI & pip stuff && torchvision
WORKDIR /tmp
ARG TBB_BASEURL=https://github.com/oneapi-src/oneTBB/releases/download
ARG TBB_VERSION=4.4.5
ARG TBB_DIR=tbb44_20160526oss
ARG TBB_SAVEPATH="/tmp/tbb.tgz"
ARG TBB_LIB_DIR="intel64/gcc4.4"
ARG TBBROOT=/tmp/$TBB_DIR
ENV JUPYTER_CONFIG_DIR=/run/determined/jupyter/config JUPYTER_DATA_DIR=/run/determined/jupyter/data JUPYTER_RUNTIME_DIR=/run/determined/jupyter/runtime
COPY requirements.txt /tmp
RUN wget "${TBB_BASEURL}/${TBB_VERSION}/${TBB_DIR}_lin.tgz" -O $TBB_SAVEPATH &&\
    tar -C /tmp -xf "${TBB_SAVEPATH}" &&\
    cp -R $TBBROOT/lib/$TBB_LIB_DIR/* /usr/local/lib/ &&\
    cp -R $TBBROOT/include/ /usr/local/include/ &&\
    git clone https://github.com/LingzheZhao/determinedai-container-scripts &&\
    cd determinedai-container-scripts &&\
    git checkout v0.1 &&\
    pip config set global.index-url https://mirrors.bfsu.edu.cn/pypi/web/simple &&\
    pip install -U pip &&\
    pip install determined && pip uninstall -y determined &&\
    pip install -r notebook-requirements.txt &&\
    pip install -r additional-requirements.txt &&\
    pip install cmake==${CMAKE_VERSION} &&\
    pip install taichi-nightly -i https://pypi.taichi.graphics/simple/ &&\
    pip install -r /tmp/requirements.txt &&\
    ./add_det_nobody_user.sh &&\
    ./install_libnss_determined.sh &&\
    ./update_alternatives_clang.sh ${CLANG_VER} 100
    # cd /tmp &&\
    # git clone https://github.com/pytorch/vision.git &&\
    # cd vision &&\
    # git checkout tags/v0.15.1 &&\
    # python setup.py install &&\
    # cd /tmp &&\
    # git clone https://github.com/rusty1s/pytorch_scatter &&\
    # cd pytorch_scatter &&\
    # git checkout tags/2.1.1 && python setup.py install &&\
    # rm -rf /tmp/*

# Install OpenEXR
RUN cd /tmp &&\
    wget https://github.com/AcademySoftwareFoundation/openexr/archive/refs/tags/v${OPENEXR_VERSION}.tar.gz &&\
    tar -xvzf v${OPENEXR_VERSION}.tar.gz &&\
    cd openexr-${OPENEXR_VERSION} &&\
    cmake -B build -GNinja &&\
    cmake --build build -t install &&\
    ldconfig && rm -rf /tmp/*

# Install OpenCV
RUN cd /tmp/ &&\
    wget https://github.com/opencv/opencv/archive/$OPENCV_VERSION.zip &&\
    unzip $OPENCV_VERSION.zip &&\ 
    rm $OPENCV_VERSION.zip &&\
    wget https://github.com/opencv/opencv_contrib/archive/$OPENCV_VERSION.zip &&\
    unzip ${OPENCV_VERSION}.zip &&\
    cd opencv-${OPENCV_VERSION} &&\
    cmake \
        -B /tmp/opencv-${OPENCV_VERSION}/build \
        -GNinja \
        -DCMAKE_CXX_STANDARD=17 \
        -DOPENCV_EXTRA_MODULES_PATH=/tmp/opencv_contrib-${OPENCV_VERSION}/modules \
        -DOPENCV_ENABLE_NONFREE=ON \
        -DWITH_CUDA=ON \
        -DCUDA_ARCH_BIN=8.9 \
        -DCMAKE_BUILD_TYPE=RELEASE \
        -DCMAKE_INSTALL_PREFIX=/usr/local &&\
    cmake --build build -t install &&\
    ldconfig && rm -rf /tmp/*

# Install Vulkan
# RUN wget -qO - https://packages.lunarg.com/lunarg-signing-key-pub.asc | apt-key add - &&\
#     wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.239-focal.list https://packages.lunarg.com/vulkan/1.3.239/lunarg-vulkan-1.3.239-focal.list &&\
#     apt-get update &&\
#     apt-get install -y vulkan-sdk &&\
#     apt-get clean

# Pre-build NeRF-SLAM if needed
# WORKDIR /workspace
# RUN git clone https://github.com/DmitriZhao/NeRF-SLAM --recursive &&\
#     cd NeRF-SLAM &&\
#     cmake ./thirdparty/instant-ngp -B build_ngp &&\
#     cmake --build build_ngp --config RelWithDebInfo -j &&\
#     cmake ./thirdparty/gtsam -DGTSAM_BUILD_PYTHON=1 -B build_gtsam &&\
#     cmake --build build_gtsam --config RelWithDebInfo -j -t install python-install python-test &&\
#     python setup.py install
