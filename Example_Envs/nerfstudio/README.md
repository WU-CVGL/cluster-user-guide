# Nerfstudio & sdfstudio dockerfile

## Build with Makefile

The Makefile contains the target docker image tag, version and build_args (proxy server).

### Build the image only

``` bash
make build_nerf
make build_sdf
```

### Build & push the image to Harbor

``` bash
make push_nerf
make push_sdf
```
