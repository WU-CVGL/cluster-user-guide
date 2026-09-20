[English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh.md)

# Contributing documentation

This repository is the source for the cluster user guide. `README.md` and
`README.zh.md` are regular files and the canonical English and Chinese home
pages; do not recreate the former `Home.md` aliases. Keep the repository root
limited to the README, AGENTS, and CONTRIBUTING English/Chinese pairs.
The canonical compute and MCP implementation is
[`WU-CVGL/determined_cluster_mcp`](https://github.com/WU-CVGL/determined_cluster_mcp);
do not add links to its retired repository name.

- Put guide chapters and the sidebars under `docs/`. Preserve page basenames
  and stable section anchors, and use real relative Markdown paths in
  `docs/_Sidebar.md` and `docs/_Sidebar.zh.md`. Put page images in
  `docs/assets/<page-name>/`, environment examples in `examples/environments/`,
  and other structured examples under the appropriate `examples/` subfolder.
- Add or rename chapters as an English/Chinese pair: `docs/Page.md` and
  `docs/Page.zh.md`. Both pages need a language switch linking both versions
  within the first eight lines. Chinese pages should link Chinese internal
  pages when a translation exists. Keep all relative links correct after moves.
- The GitHub automatic slug of each English level-two or deeper heading is its
  canonical stable fragment. Do not duplicate that ID with an English HTML
  anchor. Immediately before the corresponding Chinese section, add the
  English slug explicitly, for example `<a id="shared-storage"></a>`. If an
  English heading changes, update inbound links and its Chinese anchor.
- Translate the complete meaning of each page. Keep commands, file paths,
  configuration keys, API/tool names, field names, numeric thresholds, and
  code blocks technically identical unless a verified platform difference is
  being documented. Update both languages in one change.

- Treat resource availability, service status, network routes, and other live
  facts as dynamic. Verify them read-only with the responsible administrator,
  record when they were checked, and do not infer them from old examples.
- Keep a working compatibility path until its replacement is verified in the
  deployed environment. For example, retain the current Harbor BuildKit route
  until a builder using the explicit CA trust is proven.
- Mark historical or unverified container examples clearly. Do not present an
  image, package set, proxy, or resource pool as a default until it is tested.
- Never commit credentials, private keys, access tokens, or credential-bearing
  URLs. Use placeholders in commands and examples.

Before opening a change, install the checker's only Python dependency and run:

```bash
python -m pip install "PyYAML>=6,<7"
python scripts/check_docs.py
```

The checker is offline: it validates the root/docs layout, local Markdown links
and anchors, Wiki extensionless links (including dotted names such as
`Page.zh`), directory links, bilingual pairing and navigation, stable section
anchors, retired repository references, and JSON/YAML syntax without requesting
external URLs.
