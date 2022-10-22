# Welcome to the Wiki.

## Introduction

Currently we are hosting these services (available after [configuring the `hosts`](https://git.cvgl.lab/Cluster_User_Group/cluster-user-guide/wiki/Getting_started#user-content-setting-up-the-hosts-file)):

[Determined AI - Distributed Deep Learning and Hyperparameter Tuning Platform](https://gpu.cvgl.lab/)

[Gitea - Git with a cup of tea](https://git.cvgl.lab/)

[Nextcloud - File storage and sharing](https://pan.cvgl.lab/)

Shared Folders:

https://pan.cvgl.lab/s/6P8EyrewEz4G3sm

## Quick guide

[Tutorials Overview](https://git.cvgl.lab/Cluster_User_Group/cluster-user-guide/wiki/Tutorials)

[Getting Started](https://git.cvgl.lab/Cluster_User_Group/cluster-user-guide/wiki/Getting_started)

[Determined-AI User Guide](https://git.cvgl.lab/Cluster_User_Group/cluster-user-guide/wiki/Determined_AI_User_Guide)

[Custom Containerized Environment](https://git.cvgl.lab/Cluster_User_Group/cluster-user-guide/wiki/Custom_Containerized_Environment)

## Cluster Information
Our cluster is located at the core server room, ground floor of building E6, Yungu Campus (云谷校区-E6-1楼-核心机房), currently has `4` GPU nodes and `1` storage & management node active.

We have been designated with an IP address range: `10.0.1.66-94/27`

The specifics of the cluster nodes are as follows:

GPU Node 1：

|  Name  |  Spec  |
| :----: | :----  |
|  Model | Powerleader PR4908R (Supermicro 4124GS-TNR)|
|  CPU   | AMD EPYC 7302*2 (32C/64T, 3.0-3.3GHz)|
| Memory | Samsung DDR4 256G (16G*16) 2933MHz ECC REG|
|  GPU   | MSI RTX 3090 Turbo * 8 |
|  SSD   | Intel P4510 2TB * 1 |
|  NIC   | Intel 82599 10GbE   |

GPU Node 2, 3, 4:

|  Name  |  Spec  |
| :----: | :----  |
|  Model | Powerleader PR4908R (Supermicro 4124GS-TNR)|
|  CPU   | AMD EPYC 7402*2 (48C/96T, 2.8-3.35GHz)|
| Memory | SK Hynix / Samsung / Samsung DDR4 512G (32G*16) 3200MHz ECC REG|
|  GPU   | NVIDIA / MSI / MSI RTX 3090 * 8 |
|  SSD   | Intel P4510 2TB * 1 |
|  NIC   | Intel 82599 10GbE   |

Storage & Management node

|  Name  |  Spec  |
| :----: | :----  |
|  Model | Powerleader PR4224AK (Supermicro H11SSL)|
|  CPU   | AMD EPYC 7302*2 (32C/64T, 3.0-3.3GHz)|
| Memory | Samsung DDR4 256G (16G*16) 2933MHz ECC REG |
|  SSD   | Samsung 970 EVO Plus 500G * 1|
|  SSD   | Intel S4510 1.92TB * 2 |
|  HDD   | Seagate Exos X18 18TB * 14 |
|  NIC   | Intel 82599 10GbE Dual Port |

<details>
<summary> Click to show photo </summary>
<img src="./Home/rack.jpg" alt="drawing" style="height:50vh;"/>
<img src="./Home/gpus.jpg" alt="drawing" style="height:50vh;"/>
</details>

## Notes

### DRAM models

> Samsung 2933: M393A2K43DB2-CVF

> Samsung 3200: M393A4K40DB3-CWE

> SK Hynix 3200: HMA84GR7DJR4N-XN