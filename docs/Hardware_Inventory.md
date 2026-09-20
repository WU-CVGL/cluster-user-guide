# Hardware inventory

[English](Hardware_Inventory.md) | [简体中文](Hardware_Inventory.zh.md)

[Home](../README.md) · [Cluster reference](Cluster_Reference.md)

This is a static reference for installed equipment, not a live count of healthy or available resources. Query Determined before choosing a pool or launching a task.

The specifics of the cluster nodes are as follows:

GPU Node 1：

|  Name  |  Spec  |
| :----: | :----  |
|  Model | Powerleader PR4908R (Supermicro 4124GS-TNR)|
|  CPU   | AMD EPYC 7302 * 2 (32C/64T, 3.0-3.3GHz)|
|  RAM   | Samsung M393A2K43DB2-CVF DDR4 256G (16G*16) 2933MT/s ECC REG|
|  GPU   | MSI (0x1462) RTX 3090 Turbo * 8 |
|  SSD   | Intel P4510 2TB (U.2 PCIe 3.1) * 1 |
|  NIC   | Intel I350-T2 1GbE Dual Port|
|  NIC   | Mellanox ConnectX-4 VPI EDR QSFP28 MCX455A-ECAT 100Gb ETH/IB Single Port|
|  RAID  | LSI MegaRAID SAS-3 3108 |

GPU Node 2:

|  Name  |  Spec  |
| :----: | :----  |
|  Model | Powerleader PR4908R (Supermicro 4124GS-TNR)|
|  CPU   | AMD EPYC 7402 * 2 (48C/96T, 2.8-3.35GHz)|
|  RAM   | SK Hynix HMA84GR7DJR4N-XN DDR4 512G (32G*16) 3200MT/s ECC REG|
|  GPU   | MANLI (NVIDIA/0x10DE) RTX 4090 * 8 |
|  SSD   | Intel P4510 2TB (U.2 PCIe 3.1) * 1 |
|  SSD   | Kioxa CD6 7.68TB (U.2 PCIe 4.0) * 1 |
|  NIC   | Intel I350-T2 1GbE Dual Port|
|  NIC   | Mellanox ConnectX-4 VPI EDR QSFP28 MCX455A-ECAT 100Gb ETH/IB Single Port|

GPU Node 3, 4:

|  Name  |  Spec  |
| :----: | :----  |
|  Model | Powerleader PR4908R (Supermicro 4124GS-TNR)|
|  CPU   | AMD EPYC 7402 * 2 (48C/96T, 2.8-3.35GHz)|
|  RAM   | Samsung M393A4K40DB3-CWE DDR4 512G (32G*16) 3200MT/s ECC REG|
|  GPU   | MSI (0x1462) RTX 3090 * 8 |
|  SSD   | Intel P4510 2TB (U.2 PCIe 3.1) * 1 |
|  NIC   | Intel I350-T2 1GbE Dual Port|
|  NIC   | Mellanox ConnectX-4 VPI EDR QSFP28 MCX455A-ECAT 100Gb ETH/IB Single Port|

GPU Node 5:

|  Name  |  Spec  |
| :----: | :----  |
|  Model | ASUS ESC8000A-E11|
|  CPU   | AMD EPYC 7543 * 2 (64C/128T, 2.8-3.7GHz)|
|  RAM   | Samsung M393A4K40EB3-CWE DDR4 512G (32G*16) 3200MT/s ECC REG|
|  GPU   | MANLI (NVIDIA/0x10DE) RTX 4090 * 8 |
|  SSD   | Intel S4610 (SSDSC2KG96) 960G (SATA) (RAID 1) * 2|
|  NIC   | Intel I350-T4 1GbE Quad Port|
|  NIC   | Mellanox ConnectX-4 VPI EDR QSFP28 MCX455A-ECAT 100Gb ETH/IB Single Port|
|  RAID  | LSI SAS3008 PCI-Express Fusion-MPT SAS-3 |

GPU Node 6, 7:

|  Name  |  Spec  |
| :----: | :----  |
|  Model | ASUS ESC8000A-E12|
|  CPU   | AMD EPYC 9554 * 2 (128C/256T, 3.1-3.75GHz)|
|  RAM   | Samsung M321R8GA0BB0-CQKZJ / Micron MTC40F2046S1RC48BA1 DDR5 1536G (64G*24) 4800MT/s ECC REG|
|  GPU   | MSI (NVIDIA/0x10DE) RTX 4090 * 8 |
|  SSD   | Samsung PM9A3 1.92T (U.2 PCIe 4.0) * 1|
|  NIC   | Intel I350-AM2 1GbE Dual Port |
|  NIC   | Mellanox ConnectX-4 VPI EDR QSFP28 MCX455A-ECAT 100Gb ETH/IB Single Port|

GPU Node 8:

|  Name  |  Spec  |
| :----: | :----  |
|  Model | ASUS ESC8000A-E12|
|  CPU   | AMD EPYC 9554 * 2 (128C/256T, 3.1-3.75GHz)|
|  RAM   | SK Hynix HMCG94AEBRA109N DDR5 1536G (64G*24) 4800MT/s ECC REG|
|  GPU   | NVIDIA (0x10de) RTX 6000 Ada Generation 48G * 8 |
|  SSD   | Samsung PM9A3 (MZQL21T9HCJR-00A07) 1.92TB 2.5" NVMe U.2 drive * 2|
|  NIC   | Mellanox ConnectX-6 VPI NIC; HDR100, EDR IB/100GbE; dual-port QSFP56; PCIe4.0 x16; (MCX653106A-ECAT)|
|  NIC   | Intel I350-T2 1GbE Dual Port |

Storage Server

|  Name  |  Spec  |
| :----: | :----  |
|  Model | Powerleader PR4224AK (Supermicro H11SSL)|
|  CPU   | AMD EPYC 7302 (16C/32T, 3.0-3.3GHz)|
|  RAM   | Samsung M393A4K40DB2-CWE DDR4 256G (32G*8) 2933MT/s ECC REG |
|  SSD   | INTEL 760p (SSDPEKKW256G8) 256G (M.2 PCIe 3.0) * 1|
|  SSD   | Intel S4510 1.92TB (SATA) * 2 |
|  SSD   | WD Ultrastar DC SN640 (WUS4BB076D7P3E3) 7.68TB (U.2 PCIe 3.0) * 12 |
|  HDD   | Seagate Exos X18 18TB * 24 |
|  NIC   | Intel i210 1GbE * 2 |
|  NIC   | Mellanox ConnectX-4 VPI EDR QSFP28 MCX455A-ECAT 100Gb ETH/IB Single Port|
|  RAID  | LSI SAS3008 PCI-Express Fusion-MPT SAS-3 |

Storage Server (2U, SSD-only):

|  Name  |  Spec  |
| :----: | :----  |
|  Model | Dell PowerEdge R7525|
|  CPU   | AMD EPYC 7313 * 2  (32C/64T, 3.0-3.7GHz)|
|  RAM   | Samsung DDR4 ECC REG 3200MHz 512G (32G * 16)|
|  SSD   | KIOXIA DC CD7 RI 960GB 2.5" NVMe U.2 drive|
|  NIC   | Broadcom BCM5720 Gigabit Ethernet * 2|
|  NIC   | Mellanox ConnectX-6 VPI NIC; HDR100, EDR IB/100GbE; dual-port QSFP56; PCIe4.0 x16; (MCX653106A-ECAT)|

Management Server

|  Name  |  Spec  |
| :----: | :----  |
|  Model | ASUS RS520-E9-RS8 V2 |
|  CPU   | Intel Xeon Silver 4210R * 2 (20C/40T, 2.4-3.2GHz) |
|  RAM   | Samsung M393A4K40EB3-CWE DDR4 64G (32G*2) 3200MT/s @ 2400MT/s ECC REG |
|  SSD   | Intel S4610 (SSDSC2KG96) 960G * 2 (SATA) (RAID 1) |
|  NIC   | Intel i350-AM2 1GbE Dual Port |
|  NIC   | Mellanox ConnectX-4 VPI EDR QSFP28 MCX455A-ECAT 100Gb ETH/IB Single Port|
|  RAID  | LSI SAS3008 PCI-Express Fusion-MPT SAS-3 |

Switch

|  Brand          |  Model & Spec  |
|  :----:         | :---- |
| NVIDIA Mellanox | Spectrum SN2700 100GbE 1U Open Ethernet Switch with NVIDIA Onyx, 32 QSFP28 ports, 2 PSU, x86 CPU, Standard depth |


<details>
<summary> Click to show photo </summary>
<img src="assets/Home/rack.jpg" alt="drawing" style="height:50vh;"/>
<img src="assets/Home/rack2.jpg" alt="drawing" style="height:50vh;"/>
<img src="assets/Home/gpus.jpg" alt="drawing" style="height:50vh;"/>
<img src="assets/Home/gpus2.jpg" alt="drawing" style="height:50vh;"/>
<img src="assets/Home/gpus3.jpg" alt="drawing" style="height:50vh;"/>
</details>
