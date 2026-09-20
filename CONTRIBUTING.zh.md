[English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh.md)

# 参与文档维护

本仓库是集群用户指南的源仓库。移动页面时，应保留兼容 GitHub Wiki 的页面名和
`_Sidebar.md` 无扩展名链接。`README.md` 是指向英文首页 `Home.md` 的符号链接，
`README.zh.md` 指向 `Home.zh.md`；保留这些别名，不要维护重复页面。计算与 MCP 功能由以下仓库维护：
[`WU-CVGL/determined_cluster_mcp`](https://github.com/WU-CVGL/determined_cluster_mcp)，
不要再引用已经停用的旧仓库名。

- 新增或重命名 Markdown 页面时，同时维护 `Page.md` 和 `Page.zh.md`。两个页面
  的前八行内都必须提供英中双向切换。已有中文译文时，中文页面的内部链接应优先
  指向中文页面。
- 每个英文二级及更深标题的 GitHub 自动 slug 是该章节的规范稳定片段。不要在
  英文页中再添加同名 HTML 锚点，避免重复 ID。在对应中文章节前紧邻加入该英文
  slug，例如 `<a id="shared-storage"></a>`。英文标题变化时，同时更新入站链接和
  中文锚点。
- 中文页面应完整表达英文页面的内容。除非在记录已经核实的平台差异，否则命令、
  文件路径、配置键、API/工具名、字段名、数值阈值和代码块必须保持技术上一致。
  修改时同时更新两种语言。
- 资源可用性、服务状态、网络路由等实时事实会发生变化。应通过只读方式向负责的
  管理员核实，记录核验日期，不从旧示例推断当前状态。
- 在替代方案于实际部署中通过验证之前，保留可工作的兼容路径。例如，在使用显式
  CA 信任的 builder 验证成功前，保留当前 Harbor BuildKit 兼容路径。
- 清楚标记历史或未验证的容器示例。镜像、软件包集合、代理或资源池未通过测试前，
  不得作为默认方案推荐。
- 不得提交凭据、私钥、访问令牌或包含凭据的 URL。命令和示例中使用占位符。

提交变更前，安装检查脚本唯一的 Python 依赖并运行：

```bash
python -m pip install "PyYAML>=6,<7"
python scripts/check_docs.py
```

检查器完全离线：它检查本地 Markdown 链接与锚点、Wiki 无扩展名链接（包括
`Home.zh` 这样的带点页面名）、目录链接、双语配对与导航、稳定章节锚点、旧仓库
引用以及 JSON/YAML 语法，不会请求外部 URL。
