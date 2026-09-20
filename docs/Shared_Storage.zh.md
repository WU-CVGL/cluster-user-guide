<a id="shared-storage"></a>
# 共享存储

[English](Shared_Storage.md) | [简体中文](Shared_Storage.zh.md)

集群任务应把代码、数据、软件包、检查点、日志和结果保存在获准使用的共享存储上。个人计算机无需挂载这些文件系统：可以通过 SSH 经登录节点传输文件。

![存储模型](assets/Getting_started/storage_model.svg)

<a id="storage-roots"></a>
## 存储根目录

集群提供以下根目录名称。不同根目录的访问权限、配额、性能、保留和备份策略可能不同，也可能发生变化；选择前请确认当前策略。

| 根目录 | 需要向管理员确认的常见用途 |
| --- | --- |
| `/datasets` | 共享或整理后的数据集；部分区域可能只读 |
| `/workspace` | 用户或项目工作区，通常位于分配的子目录下 |
| `/SSD` | SSD 存储 |
| `/SSD_home` | SSD 用户或项目存储 |
| `/SSD_datasets` | SSD 数据集存储 |
| `/SSD3` | SSD 存储 |
| `/SSD3_home` | SSD 用户或项目存储 |
| `/SSD3_datasets` | SSD 数据集存储 |
| `/UNSAFE_SSD4` | 必须明确确认当前耐久性和使用策略的存储 |

根目录名称并不表示它可写、已备份、有快照、永久保留，或适合保存珍贵数据的唯一副本。如果已记录的保留或备份策略不能满足需求，请保留独立副本。

<a id="three-path-namespaces"></a>
## 三种路径命名空间

不要混淆以下命名空间：

| 命名空间 | 含义 |
| --- | --- |
| 集群主机路径 | 登录节点或 Determined agent 可见的路径，例如 `/workspace/USER/project` |
| 容器路径 | 由 `bind_mounts[].container_path` 声明、供工作负载使用的绝对路径 |
| 客户端本地路径 | 笔记本或工作站上的路径；可能与两种集群路径都不同 |

绑定挂载会明确规定路径转换：

```yaml
bind_mounts:
  - host_path: /workspace/USER
    container_path: /run/determined/workdir/home
  - host_path: /datasets
    container_path: /datasets
    read_only: true
  - host_path: /SSD3_home
    container_path: /SSD3_home
```

在容器内，请使用声明的 `container_path`。它是绝对路径，无需位于 `/run/determined/workdir` 或任务当前工作目录之下。实际提交配置中的映射是权威依据。

<a id="permissions-and-read-only-data"></a>
## 权限与只读数据

长时间运行任务前，请从登录节点检查实际目录及其父目录：

```bash
ssh cvgl-login 'id; ls -ld /workspace/USER /datasets'
```

不要假设可读数据集同时可写。只修改由你管理的目录权限。应使用分配的可写目录或项目用户组，不要使用 `chmod -R 777` 等过于宽泛的权限模式。

部分 NFS/NAS 导出会拒绝保留所有者、用户组、权限或目录时间。失败的 rsync 可能在已复制部分文件后返回退出码 23。重新运行前，请检查输出并修正原因。如果文件系统策略确有要求，仅对相应目标使用 `--no-owner --no-group --no-perms --omit-dir-times`；不要把这些参数盲目设为全局默认值。

<a id="stage-files-through-the-login-node"></a>
## 通过登录节点传输文件

使用[入门指南](Getting_started.zh.md#5-configure-a-stable-ssh-alias)中配置的 SSH 别名。先预览；除非已仔细检查目标，否则不要使用 `--delete`：

```bash
rsync -a --safe-links --itemize-changes --dry-run \
  --exclude='.git/' --exclude='.env*' --exclude='.secrets*' \
  --exclude='.ssh/' --exclude='.aws/' --exclude='*.pem' --exclude='*.key' \
  "$PWD/project/" cvgl-login:/workspace/USER/project/

rsync -a --safe-links --itemize-changes \
  --exclude='.git/' --exclude='.env*' --exclude='.secrets*' \
  --exclude='.ssh/' --exclude='.aws/' --exclude='*.pem' --exclude='*.key' \
  "$PWD/project/" cvgl-login:/workspace/USER/project/
```

源目录末尾的斜杠表示复制目录内容。即使不使用 `--delete`，rsync 仍可能替换目标中同名文件。这里的排除规则只是起点，并非完整的 secret 扫描器：传输前请检查项目特有的凭据、缓存和机器本地状态。不要把密码或 token 放进命令、任务配置、日志或报告。

反向操作即可取回结果：

```bash
mkdir -p "$PWD/results"
rsync -a --safe-links --itemize-changes --dry-run \
  cvgl-login:/workspace/USER/run/results/ "$PWD/results/"
```

检查逐项变更后，才移除 `--dry-run`。GUI SFTP 客户端适合小型传输；请参阅[网络与远程访问](Network_and_Remote_Access.zh.md#file-transfer-clients)。

<a id="use-shared-paths-in-determined"></a>
## 在 Determined 中使用共享路径

启动前，请把源代码、配置、数据和本地提供的软件包放到共享存储上，并为检查点、日志和输出选择共享路径。运行时依赖也可以安装在容器镜像中。持久运行应使用基于稳定修订版本的独立目录；交互式调试 shell 可以使用可变工作区。

通过 `bind_mounts`、任务命令以及相应的检查点/输出设置引用这些路径。不要通过实验的 `modelDefinition`、项目归档、文件上下文或 project-root 选项上传代码或数据。共享存储是文件传输与持久化边界。

任务配置请参阅 [Determined AI 用户指南](Determined_AI_User_Guide.zh.md)，镜像和依赖请参阅[自定义容器环境](Custom_Containerized_Environment.zh.md)。

<a id="before-relying-on-a-storage-root"></a>
## 依赖某个存储根目录之前

请通过当前文档或管理员确认以下各项：

- 分配给你的可写路径和用户组；
- 配额和预期文件数量限制；
- 所需 Determined 资源池是否能访问该路径；
- 备份、快照、保留和删除策略；
- 是否适合在该处运行高 I/O 工作负载；
- 运行结束后应把持久结果复制到哪里。

如果其中任何一项未知，不要根据文件系统名称或旧示例自行推断。
