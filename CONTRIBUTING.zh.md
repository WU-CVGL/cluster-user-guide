[English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh.md)

# 参与文档维护

本仓库是集群用户指南的源仓库。`README.md` 和 `README.zh.md` 是普通文件，
分别作为规范的英中首页；不要恢复旧的 `Home.md` 别名。仓库根目录只保留
README、AGENTS 和 CONTRIBUTING 三组英中文件。计算与 MCP 功能由以下仓库维护：
[`WU-CVGL/determined_cluster_mcp`](https://github.com/WU-CVGL/determined_cluster_mcp/blob/main/README.zh.md)，
不要再引用已经停用的旧仓库名。

- 指南章节和侧栏统一放在 `docs/`。保留页面 basename 和稳定章节锚点，并在
  `docs/_Sidebar.md` 与 `docs/_Sidebar.zh.md` 中使用真实的相对 Markdown 路径。
  页面图片放在 `docs/assets/<page-name>/`，环境示例放在
  `examples/environments/`，其他结构化示例放在适当的 `examples/` 子目录。
- 新增或重命名章节时，同时维护 `docs/Page.md` 和 `docs/Page.zh.md`。两个页面的
  前八行内都必须提供英中双向切换。已有中文译文时，中文页面的内部链接应优先
  指向中文页面。移动文件后应同步修正全部相对链接。
- 每个英文二级及更深标题的 GitHub 自动 slug 是该章节的规范稳定片段。不要在
  英文页中再添加同名 HTML 锚点，避免重复 ID。在对应中文章节前紧邻加入该英文
  slug，例如 `<a id="shared-storage"></a>`。英文标题变化时，同时更新入站链接和
  中文锚点。
- 中文页面应完整表达英文页面的内容。除非在记录已有说明的平台差异，否则命令、
  文件路径、配置键、API/工具名、字段名、数值阈值和代码块必须保持技术上一致。
  修改时同时更新两种语言。
- 资源可用性、服务状态、网络路由等实时事实会发生变化。需要这些信息时，应查询
  负责的数据源，不要从旧示例推断当前状态。
- 保留当前部署所需的兼容路径。构建工具需区分客户端 CA、daemon CA 和 registry
  域名解析要求。
- 将旧容器配方视为起点。推荐为默认方案前，应审查其基础镜像、软件包集合、代理
  和资源假设。
- 不得提交凭据、私钥、访问令牌或包含凭据的 URL。命令和示例中使用占位符。

提交变更前，安装检查脚本唯一的 Python 依赖并运行：

```bash
python -m pip install "PyYAML>=6,<7"
python scripts/check_docs.py
```

检查器完全离线：它检查根目录与 `docs/` 布局、本地 Markdown 链接与锚点、Wiki
无扩展名链接（包括 `Page.zh` 这样的带点页面名）、目录链接、双语配对与导航、
稳定章节锚点、旧仓库引用以及 JSON/YAML 语法，不会请求外部 URL。
