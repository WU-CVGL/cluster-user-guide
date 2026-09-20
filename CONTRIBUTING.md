[English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh.md)

# Contributing documentation

This repository is the source for the cluster user guide. Preserve compatible
GitHub Wiki page names and extensionless `_Sidebar.md` links when moving pages;
`README.md` is a symbolic link to the canonical `Home.md`, and `README.zh.md`
links to `Home.zh.md`; keep these aliases rather than maintaining duplicate pages.
The canonical compute and MCP implementation is
[`WU-CVGL/determined_cluster_mcp`](https://github.com/WU-CVGL/determined_cluster_mcp);
do not add links to its retired repository name.

- Add or rename Markdown pages as an English/Chinese pair: `Page.md` and
  `Page.zh.md`. Both pages need a language switch linking both versions within
  the first eight lines. Chinese pages should link Chinese internal pages when
  a translation exists.
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

The checker is offline: it validates local Markdown links and anchors, Wiki
extensionless links (including dotted names such as `Home.zh`), directory
links, bilingual pairing and navigation, stable section anchors, retired
repository references, and JSON/YAML syntax without requesting external URLs.
