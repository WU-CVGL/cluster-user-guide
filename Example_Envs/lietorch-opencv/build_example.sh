docker build \
    -t lietorch-opencv-det:0.18.2.0 \
    --build-arg http_proxy=http://10.0.1.68:8889 \
    --build-arg https_proxy=http://10.0.1.68:8889 \
    .
