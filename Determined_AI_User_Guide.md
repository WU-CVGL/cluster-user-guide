<h1 align="center">Getting started with the batch system:<br>
Determined-AI User Guide </h1>
<p align="center">
2022-03-17 v0.1a
</p>

- [Introduction](#introduction)
- [User Account](#user-account)
  - [Ask for your account](#ask-for-your-account)
  - [Authentication](#authentication)
    - [WebUI](#webui)
    - [CLI](#cli)
  - [Changing passwords](#changing-passwords)
- [Submitting Tasks](#submitting-tasks)
  - [Task Configuration Template](#task-configuration-template)
  - [Submit](#submit)
  - [Managing Tasks](#managing-tasks)
  - [Experiments](#experiments)
  - [References](#references)

# Introduction

!["intro-determined-ai"](https://docs.determined.ai/latest/_static/images/logo-determined-ai.svg)

We are currently using [Determined AI](https://www.determined.ai/) to manage our GPU Cluster.

You can open the dashboard (a.k.a WebUI) by the following URL and login:

[https://gpu.cvgl.lab/](https://gpu.cvgl.lab/)


# User Account

## Ask for your account

You need to ask system `admin` to get your user account. 


## Authentication

### WebUI
The WebUI will automatically redirect users to a login page if there is no valid Determined session established on that browser. After logging in, the user will be redirected to the URL they initially attempted to access.

### CLI
Before using the CLI(Command Line Interface), you may need to recite some basics: [[Basics]](http://10.0.1.67:3000/Cluster_User_Group/cluster-user-guide/wiki/Basics)

In the CLI, the user login subcommand can be used to authenticate a user:
```
det user login <username>
```

## Changing passwords
Users have *blank* passwords by default. If desired, a user can change their own password using the user change-password subcommand:
```
det user change-password
```

# Submitting Tasks

## Task Configuration Template

Here is a template of a task configuration file, in YAML format:
```
description: <task_name>
resources:
    slots: 1
bind_mounts:
    - host_path: /workspace/<user_name>/
        container_path: /run/determined/workdir/home/
    - host_path: /datasets/
        container_path: /run/determined/workdir/data/
environment:
    image: determinedai/environments:cuda-11.3-pytorch-1.10-lightning-1.5-tf-2.8-deepspeed-0.5.10-gpu-0.17.12
```
Notes: 
- You need to change the `task_name` and `user_name` to your own
- Number of `resources.slots` is the number of GPUs you want to use
- In `bind_mounts`, the first host_path/container_path maps your workspace directory into the container; And the second maps the dataset directory (`/datasets`) into the container.
- In `environment.image`, an official image by *Determined AI* is used. *Determined AI* provides [*Docker* images](https://hub.docker.com/r/determinedai/environments/tags) that includes common deep learning libraries and frameworks. You can also [develop your custom image](https://gpu.cvgl.lab/docs/prepare-environment/custom-env.html) based on your project dependency. Notice that instead of pushing the image to Docker Hub, you can use the private registry: `registry.cvgl.lab`. For instance: 
```
    docker login -u cvgl -p westlake_liu registry.cvgl.lab    # You only need to login once
    docker tag my_image:latest  registry.cvgl.lab/my_image:latest
    docker push registry.cvgl.lab/my_image:latest
```
and use the image `registry.cvgl.lab/my_image:latest` in the task configuration `.yaml` file.

## Submit

Save the YAML configuration to, let's say, `test_task.yaml`. You can start a Jupyter Notebook (Lab) environment or a simple shell environment. A notebook is a web interface thus more user-friendly. However, you can use **Visual Studio Code** or **PyCharm** and connect to a shell environment[[3]](https://docs.determined.ai/latest/features/commands-and-shells.html#visual-studio-code), which brings more flexibility and productivity if you are familiar with these editors.

For notebook:
```
    det notebook start --config-file test_task.yaml
```
For shell:
```
    det shell start --config-file test_task.yaml
```
Now you can see your task pending/running on the WebUI dashboard.
![tasks](https://docs.determined.ai/latest/_images/task-list@2x.jpg)

## Managing Tasks

You can manage the tasks on the WebUI.

![recent-tasks](https://gpu.cvgl.lab/docs/_images/pytorch_dashboard@2x.jpg)


## Experiments

(TODO)

![experiments](https://gpu.cvgl.lab/docs/_images/hp_experiment_page@2x.jpg)


## References
[[1]](https://gpu.cvgl.lab/docs/sysadmin-basics/users.html)
[[2]](https://zhuanlan.zhihu.com/p/422462131)