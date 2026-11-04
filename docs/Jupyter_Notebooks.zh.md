<a id="jupyter-for-interactive-research"></a>
# 使用 Jupyter 进行交互式研究

[English](Jupyter_Notebooks.md) | [简体中文](Jupyter_Notebooks.zh.md)

[首页](../README.zh.md) · [任务类型选择](Determined_AI_User_Guide.zh.md)

Jupyter 是一个可选入口，适合需要反复查看中间结果的研究工作。Notebook 将可执行代码、文字说明、公式和可视化输出放在同一份文档中。可参阅 [Jupyter 官方介绍](https://docs.jupyter.org/en/latest/)。

<a id="when-to-use-it"></a>
## 适用场景

| 工作 | 示例 |
| --- | --- |
| 数据探索与检查 | 查看样本、标签、分布和异常数据 |
| 模型结果分析 | 对比检查点、绘制指标和检查失败案例 |
| 算法原型验证 | 分步检查张量、梯度、几何变换或损失函数 |
| 交互式可视化 | 调整参数，查看图像、点云或曲线 |
| 教学与研究交流 | 将解释、代码和结果一起展示 |

可重复的批量评估和 agent 执行的脚本优先使用 command；长时间或跨天训练使用 experiment。将可复用逻辑提取到 Python 模块，让 Notebook 主要负责探索和展示。分享前重启 kernel，并按顺序运行全部单元，检查是否依赖残留状态。

<a id="start-jupyterlab-in-a-shell"></a>
## 在 shell 中启动 JupyterLab

Shell 默认在 SSH 服务器旁运行 JupyterLab。请先完成 [CLI 配置](Determined_AI_User_Guide.zh.md#install-and-authenticate)；MCP 可用的任务类型以规范的[计算服务参考](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.zh.md)为准。

复制共享挂载模板：

```bash
cp examples/compute/shell.yaml jupyter.yaml
```

编辑 `jupyter.yaml`：替换用户、资源池和镜像占位符，选择带 JupyterLab 的镜像（`PATH` 中有 `jupyter`），并设置有意义的 `description`。仅做 CPU 分析时使用 `resources.slots: 0`；确实需要 GPU 时再申请。根据任务需求检查目标资源池的可调度槽位或辅助容器容量。Shell 提交可能排队。

启动 shell 时不附带文件上下文：

```bash
det shell start --detach --config-file jupyter.yaml
```

不要添加 `--context` 或 `--include`。在已映射的共享工作区中打开或创建 `.ipynb` 文件，通过共享挂载读取数据集。

列出自己的 shell 及某个 shell 的服务，`jupyter` 变为 `READY` 后打开 JupyterLab：

```bash
det shell list
det task services <shell-id>
det task open <shell-id> jupyter
```

镜像中没有 JupyterLab 时，`jupyter` 显示为 `UNAVAILABLE`，shell 继续运行。

在 WebUI 中，于 **Jobs** 页面选择 **Launch Interactive Task**，保持 **Services** 下的 **JupyterLab** 勾选，并在 **Show Full Config** 中加入 `jupyter.yaml` 的 `bind_mounts`。在 shell 页面的 **JupyterLab** 标签页中打开 JupyterLab，或从 shell 的操作菜单中选择 **Open JupyterLab**。

<a id="save-work-and-release-resources"></a>
## 保存工作并释放资源

Notebook、输入和结果均保存在[共享存储](Shared_Storage.zh.md)中。保存 `.ipynb` 文件不会保存全部 kernel 内存，所需产物应单独写入文件。关闭浏览器标签页不会停止 shell，也不会释放已分配资源。使用完毕后停止 shell：

```bash
det shell kill <shell-id>
```

**占用 GPU 的 shell 适用[回收策略](Interactive_Shell.zh.md#shell-cleanup-policy)，只使用 JupyterLab 时也是如此：** GPU 持续空闲的 shell 会先收到警告，随后被停止。仅使用 CPU 的 shell 不受此策略影响。

设置了 `idle_timeout` 的 shell 在无活动达到该时长后也会结束；正在执行的 kernel 算作活动。参阅[交互式 Shell](Interactive_Shell.zh.md#reconnect-and-stop)。
