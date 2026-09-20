# Jupyter for interactive research

[English](Jupyter_Notebooks.md) | [简体中文](Jupyter_Notebooks.zh.md)

[Home](Home.md) · [Task selection](Determined_AI_User_Guide.md)

Jupyter is an optional interface for research that benefits from inspecting intermediate results. A notebook combines runnable code, explanatory text, equations and visual output in one document. See the [Jupyter introduction](https://docs.jupyter.org/en/latest/).

## When to use it

| Work | Examples |
| --- | --- |
| Explore and check data | Inspect samples, labels, distributions and outliers |
| Analyze model results | Compare checkpoints, plot metrics and inspect failure cases |
| Prototype an algorithm | Check tensors, gradients, geometric transforms or loss functions step by step |
| Visualize interactively | Adjust parameters and inspect images, point clouds or plots |
| Teach or share research | Present explanations, code and results together |

For repeatable batch evaluation and agent-driven scripts, prefer a command. Use an experiment for long or overnight training. Move reusable logic into Python modules and keep notebooks focused on exploration and presentation. Before sharing a notebook, restart its kernel and run all cells in order to check that it does not rely on leftover state.

## Start a native Notebook task

The current MCP compute service supports `command`, `shell` and `experiment`; it does not expose a `notebook` task kind. Use the native Determined CLI for this optional workflow. Complete the [CLI setup](Determined_AI_User_Guide.md#install-and-authenticate) first.

Copy the shared-mount template:

```bash
cp examples/compute/shell.yaml notebook.yaml
```

Edit `notebook.yaml`: replace the user, pool and image placeholders, choose an image with Determined Notebook support, and set a meaningful `description`. Use `resources.slots: 0` for CPU-only analysis; request GPUs only when the analysis needs them. Check the selected pool's schedulable slots or auxiliary-container capacity as appropriate. Native Notebook submissions can queue; they do not have the MCP launch admission check.

Start the task without a file context:

```bash
det notebook start --config-file notebook.yaml
```

Do not add `--context` or `--include`. Open or create `.ipynb` files under the mapped shared workspace, and read datasets through their shared mounts.

List tasks or reopen the browser interface:

```bash
det notebook list
det notebook open <notebook-id>
```

## Save work and release resources

Keep notebooks, inputs and results on [shared storage](Shared_Storage.md). Saving an `.ipynb` file does not preserve all kernel memory; write required artifacts to files. Closing a browser tab does not stop the task or release its allocated resources. Stop your task when finished:

```bash
det notebook kill <notebook-id>
```

**Long-idle native Jupyter/Notebook tasks are currently stopped manually by the administrator.** There is no fixed automatic idle timeout promised for these tasks, and the shell watchdog policy must not be applied to them.

If you start Jupyter inside a Determined **shell**, the underlying task is still a shell and remains subject to the [shell cleanup policy](Interactive_Shell.md#verified-shell-cleanup-policy). The notebook interface does not change the task's lifecycle.
