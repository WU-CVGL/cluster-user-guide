<h1 align="center">Getting started with the batch system:<br>
Determined-AI User Guide </h1>
<p align="center">
2022-03-10 v0.1
</p>



# Introduction

!["intro-determined-ai"](https://docs.determined.ai/latest/_static/images/logo-determined-ai.svg)

We are currently using [Determined AI](https://www.determined.ai/) to manage our GPU Cluster.

You can open the dashboard (a.k.a WebUI) by the following URL and login:

[https://gpu.cvgl.lab/](https://gpu.cvgl.lab/)


# User Account [[1]](https://docs.determined.ai/latest/sysadmin-basics/users.html)

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

# Submitting Tasks [[2]](https://zhuanlan.zhihu.com/p/422462131)

## Task Configuration Template

Here is a template of a task configuration file, in YAML format:
```
description: <your_task_name>
resources:
    slots: 1
bind_mounts:
    - host_path: /workspace/<user_name>/
        container_path: /run/determined/workdir/home/
    - host_path: /datasets/
        container_path: /run/determined/workdir/data/
environment:
    image: determinedai/environments:cuda-11.1-pytorch-1.9-lightning-1.5-tf-2.4-deepspeed-0.5.10-gpu-0.17.12
```
Notes: 
- You need to change the task_name and user_name to your own
- Number of **slots** is the number of GPUs you want to use
- In **bind_mounts**, the first host_path/container_path maps your workspace directory into the container; And the second maps the dataset directory (/data) into the container.

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

![recent-tasks](https://docs.determined.ai/latest/_images/pytorch_dashboard@2x.jpg)


## Experiments

(TODO)

![experiments](https://docs.determined.ai/latest/_images/hp_experiment_page@2x.jpg)