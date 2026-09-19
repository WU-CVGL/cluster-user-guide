# Contributing documentation

This repository is the source for the cluster user guide. Preserve compatible
GitHub Wiki page names and extensionless `_Sidebar.md` links when moving pages;
`Home.md` remains the canonical home page and `README.md` may point to it.

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
extensionless links, directory links, and JSON/YAML syntax without requesting
external URLs.
