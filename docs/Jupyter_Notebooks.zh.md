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

<a id="start-a-native-notebook-task"></a>
## 启动原生 Notebook 任务

这个可选 Notebook 工作流使用原生 Determined CLI。请先完成 [CLI 配置](Determined_AI_User_Guide.zh.md#install-and-authenticate)；MCP 可用的任务类型以规范的[计算服务参考](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/docs/compute-service.zh.md)为准。

复制共享挂载模板：

```bash
cp examples/compute/shell.yaml notebook.yaml
```

编辑 `notebook.yaml`：替换用户、资源池和镜像占位符，选择支持 Determined Notebook 的镜像，并设置有意义的 `description`。仅做 CPU 分析时使用 `resources.slots: 0`；确实需要 GPU 时再申请。根据任务需求检查目标资源池的可调度槽位或辅助容器容量。原生 Notebook 提交可能排队。

启动时不附带文件上下文：

```bash
det notebook start --config-file notebook.yaml
```

不要添加 `--context` 或 `--include`。在已映射的共享工作区中打开或创建 `.ipynb` 文件，通过共享挂载读取数据集。

查看任务或重新打开浏览器界面：

```bash
det notebook list
det notebook open <notebook-id>
```

<a id="save-work-and-release-resources"></a>
## 保存工作并释放资源

Notebook、输入和结果均保存在[共享存储](Shared_Storage.zh.md)中。保存 `.ipynb` 文件不会保存全部 kernel 内存，所需产物应单独写入文件。关闭浏览器标签页不会停止任务，也不会释放已分配资源。使用完毕后停止任务：

```bash
det notebook kill <notebook-id>
```

**目前，长时间空闲的原生 Jupyter/Notebook 任务由管理员手动停止（kill）。** 这些任务没有约定固定的自动空闲超时，不能套用 shell 的 watchdog 回收策略。

如果在 Determined **shell** 内启动 Jupyter，底层任务仍然是 shell，依然受 [shell 回收策略](Interactive_Shell.zh.md#shell-cleanup-policy)管理。Notebook 界面不会改变任务的生命周期。
