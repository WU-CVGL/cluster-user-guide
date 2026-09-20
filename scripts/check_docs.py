#!/usr/bin/env python3
"""Check local documentation links, anchors, and structured examples.

The checker is deliberately offline.  It understands both this repository's
Markdown layout and its GitHub Wiki compatibility links.
"""

from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import html
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable, Iterator
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:  # pragma: no cover - exercised by users without the CI dependency
    yaml = None


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_SUFFIXES = {".md", ".markdown"}
YAML_SUFFIXES = {".yaml", ".yml"}
LANGUAGE_SWITCH_LINES = 8
OLD_MCP_REPOSITORY = re.compile(
    r"(?:https?://github\.com/)?(?:WU-CVGL|LingzheZhao)/determined_batch_submit\b", re.IGNORECASE
)
STABLE_ANCHOR_ID = re.compile(r"^[a-z0-9](?:[a-z0-9_-]*[a-z0-9])?$")

INLINE_LINK = re.compile(
    r"!?\[[^\]]*\]\(\s*(?P<target><[^>]+>|[^\s)]+)", re.MULTILINE
)
REFERENCE_LINK = re.compile(
    r"^\s{0,3}\[[^\]]+\]:\s*(?P<target><[^>]+>|\S+)", re.MULTILINE
)
HTML_LINK = re.compile(
    r"\b(?:href|src)\s*=\s*[\"'](?P<target>[^\"']+)[\"']", re.IGNORECASE
)
ATX_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(?P<text>.*?)\s*#*\s*$")
SETEXT_UNDERLINE = re.compile(r"^\s*(?:=+|-+)\s*$")
HTML_ANCHOR = re.compile(
    r"<(?:a|[a-z][a-z0-9:-]*)\b[^>]*\b(?:id|name)\s*=\s*[\"'](?P<id>[^\"']+)[\"']",
    re.IGNORECASE,
)
HTML_HEADING = re.compile(
    r"<h[1-6]\b[^>]*>(?P<text>.*?)</h[1-6]>", re.IGNORECASE | re.DOTALL
)
STANDALONE_HTML_ANCHOR = re.compile(
    r"^\s*<a\s+(?:id|name)\s*=\s*[\"'](?P<id>[^\"']+)[\"']\s*></a>\s*$",
    re.IGNORECASE,
)
TAG = re.compile(r"<[^>]+>")
MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
MARKDOWN_LINK_TEXT = re.compile(r"\[([^\]]+)\]\([^)]*\)")


def repository_files() -> list[Path]:
    """Return tracked and not-yet-added, non-ignored repository files."""

    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths: list[Path] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        path = ROOT / raw.decode("utf-8", errors="surrogateescape")
        if path.is_symlink() or path.is_file():
            paths.append(path)
    return sorted(set(paths))


def without_fenced_code(text: str) -> str:
    """Blank fenced code while preserving line numbers."""

    output: list[str] = []
    fence: str | None = None
    for line in text.splitlines(keepends=True):
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        marker = match.group(1) if match else None
        if fence is None and marker is not None:
            fence = marker[0]
            output.append("\n" if line.endswith("\n") else "")
        elif fence is not None:
            output.append("\n" if line.endswith("\n") else "")
            if marker is not None and marker[0] == fence:
                fence = None
        else:
            output.append(line)
    return "".join(output)


def link_targets(text: str) -> Iterator[tuple[int, str]]:
    visible = without_fenced_code(text)
    matches = [
        *INLINE_LINK.finditer(visible),
        *REFERENCE_LINK.finditer(visible),
        *HTML_LINK.finditer(visible),
    ]
    for match in sorted(matches, key=lambda item: item.start()):
        target = match.group("target")
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        yield visible.count("\n", 0, match.start()) + 1, html.unescape(target)


def slugify(value: str) -> str:
    value = MARKDOWN_IMAGE.sub(r"\1", value)
    value = MARKDOWN_LINK_TEXT.sub(r"\1", value)
    value = TAG.sub("", value)
    value = re.sub(r"[`*_~]", "", html.unescape(value)).strip().lower()
    value = re.sub(r"[^\w\- ]", "", value, flags=re.UNICODE)
    return re.sub(r"\s+", "-", value)


@lru_cache(maxsize=None)
def anchors(path: Path) -> frozenset[str]:
    text = path.read_text(encoding="utf-8")
    result: set[str] = set()
    counts: Counter[str] = Counter()
    in_fence = False
    fence_character: str | None = None
    lines = text.splitlines()
    previous: str | None = None

    def add_heading(raw: str) -> None:
        base = slugify(raw)
        if not base:
            return
        occurrence = counts[base]
        counts[base] += 1
        result.add(base if occurrence == 0 else f"{base}-{occurrence}")

    for line in lines:
        fence = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            character = fence.group(1)[0]
            if not in_fence:
                in_fence = True
                fence_character = character
            elif character == fence_character:
                in_fence = False
                fence_character = None
            previous = None
            continue
        if in_fence:
            continue
        for match in HTML_ANCHOR.finditer(line):
            result.add(html.unescape(match.group("id")))
        match = ATX_HEADING.match(line)
        if match:
            add_heading(match.group("text"))
        elif previous and SETEXT_UNDERLINE.match(line):
            add_heading(previous.strip())
        previous = line if line.strip() else None

    for match in HTML_HEADING.finditer(without_fenced_code(text)):
        add_heading(match.group("text"))
    return frozenset(result)


def resolve_local_target(source: Path, raw_target: str) -> tuple[Path | None, str | None]:
    target = raw_target.strip()
    if not target or target.startswith("#"):
        return source, unquote(target[1:]) if target.startswith("#") else None
    if target.startswith("//"):
        return None, None
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None, None

    decoded = unquote(parsed.path)
    if not decoded:
        return source, unquote(parsed.fragment) or None
    candidate = (ROOT / decoded.lstrip("/")) if decoded.startswith("/") else (source.parent / decoded)

    # GitHub Wiki page links omit .md.  Prefer the page over an asset directory
    # with the same name (for example Home.md versus Home/).
    if not decoded.endswith("/"):
        # Appending is intentional: Home.zh is a Wiki page name for
        # Home.zh.md, not a request to replace the .zh suffix with .md.
        markdown_candidate = Path(str(candidate) + ".md")
        if markdown_candidate.exists():
            candidate = markdown_candidate
    return candidate, unquote(parsed.fragment) or None


def check_markdown(files: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    for source in files:
        text = source.read_text(encoding="utf-8")
        for line, raw_target in link_targets(text):
            target, fragment = resolve_local_target(source, raw_target)
            if target is None:
                continue
            if not target.exists():
                errors.append(
                    f"{source.relative_to(ROOT)}:{line}: missing local target {raw_target!r}"
                )
                continue
            if not target.resolve().is_relative_to(ROOT):
                errors.append(
                    f"{source.relative_to(ROOT)}:{line}: local target escapes repository "
                    f"{raw_target!r}"
                )
                continue
            if fragment and target.suffix.lower() in MARKDOWN_SUFFIXES:
                normalized = fragment.removeprefix("user-content-")
                available = anchors(target.resolve())
                if normalized not in available:
                    errors.append(
                        f"{source.relative_to(ROOT)}:{line}: missing anchor "
                        f"#{fragment} in {target.relative_to(ROOT)}"
                    )
    return errors


def check_structured_files(files: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    for path in files:
        suffix = path.suffix.lower()
        if suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        elif suffix in YAML_SUFFIXES or path.name == ".condarc":
            if yaml is None:
                errors.append("PyYAML is required: install with `python -m pip install PyYAML`")
                break
            try:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, yaml.YAMLError) as exc:
                errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
    return errors


def check_symlinks(files: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    for path in files:
        if not path.is_symlink():
            continue
        if not path.exists():
            errors.append(f"{path.relative_to(ROOT)}: broken symbolic link")
        elif not path.resolve().is_relative_to(ROOT):
            errors.append(f"{path.relative_to(ROOT)}: symbolic link escapes repository")
    return errors


def paired_markdown(path: Path) -> Path:
    """Return the English/Chinese counterpart for a Markdown path."""

    suffix = path.suffix
    if path.stem.endswith(".zh"):
        return path.with_name(path.stem.removesuffix(".zh") + suffix)
    return path.with_name(path.stem + ".zh" + suffix)


def is_chinese_page(path: Path) -> bool:
    return path.stem.endswith(".zh")


def markdown_paths(files: Iterable[Path]) -> list[Path]:
    return sorted(
        path
        for path in files
        if path.exists() and path.suffix.lower() in MARKDOWN_SUFFIXES
    )


def check_language_pairs(files: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    markdown = markdown_paths(files)
    available = set(markdown)
    for path in markdown:
        pair = paired_markdown(path)
        if pair not in available:
            errors.append(
                f"{path.relative_to(ROOT)}: missing language pair "
                f"{pair.relative_to(ROOT)}"
            )
    return errors


def check_readme_aliases() -> list[str]:
    errors: list[str] = []
    expected = {
        ROOT / "README.md": ROOT / "Home.md",
        ROOT / "README.zh.md": ROOT / "Home.zh.md",
    }
    for alias, target in expected.items():
        if not alias.is_symlink():
            errors.append(f"{alias.relative_to(ROOT)}: must be a symbolic link to {target.name}")
        elif not alias.exists() or alias.resolve() != target.resolve():
            errors.append(f"{alias.relative_to(ROOT)}: must resolve to {target.name}")
    return errors


def check_language_switches(files: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    for path in markdown_paths(files):
        if path.is_symlink():
            continue
        pair = paired_markdown(path)
        top = "\n".join(path.read_text(encoding="utf-8").splitlines()[:LANGUAGE_SWITCH_LINES])
        targets: set[Path] = set()
        for _line, raw_target in link_targets(top):
            target, _fragment = resolve_local_target(path, raw_target)
            if target is not None and target.exists():
                targets.add(target.resolve())
        required = {path.resolve(), pair.resolve()}
        if not required.issubset(targets):
            errors.append(
                f"{path.relative_to(ROOT)}: top {LANGUAGE_SWITCH_LINES} lines must link "
                f"both {path.name} and {pair.name}"
            )
    return errors


def explicit_anchor_ids(path: Path) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    for line_number, line in enumerate(
        without_fenced_code(path.read_text(encoding="utf-8")).splitlines(), start=1
    ):
        match = STANDALONE_HTML_ANCHOR.match(line)
        if match:
            result.append((line_number, html.unescape(match.group("id"))))
    return result


def english_section_ids(path: Path) -> list[tuple[int, str]]:
    """Return GitHub-style automatic IDs for level-two and deeper headings."""

    result: list[tuple[int, str]] = []
    counts: Counter[str] = Counter()
    lines = without_fenced_code(path.read_text(encoding="utf-8")).splitlines()
    previous: tuple[int, str] | None = None

    def add(line_number: int, raw: str, level: int) -> None:
        base = slugify(raw)
        if not base:
            return
        occurrence = counts[base]
        counts[base] += 1
        anchor_id = base if occurrence == 0 else f"{base}-{occurrence}"
        if level >= 2:
            result.append((line_number, anchor_id))

    for line_number, line in enumerate(lines, start=1):
        heading = ATX_HEADING.match(line)
        if heading:
            stripped = line.lstrip()
            level = len(stripped) - len(stripped.lstrip("#"))
            add(line_number, heading.group("text"), level)
            previous = None
        elif previous and SETEXT_UNDERLINE.match(line):
            level = 1 if line.lstrip().startswith("=") else 2
            add(previous[0], previous[1], level)
            previous = None
        else:
            previous = (line_number, line.strip()) if line.strip() else None
    return result


def check_stable_section_anchors(files: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    markdown = markdown_paths(files)
    for path in markdown:
        if path.is_symlink():
            continue
        explicit = explicit_anchor_ids(path)
        counts = Counter(anchor_id for _line, anchor_id in explicit)
        for line_number, anchor_id in explicit:
            if not STABLE_ANCHOR_ID.fullmatch(anchor_id):
                errors.append(
                    f"{path.relative_to(ROOT)}:{line_number}: unstable HTML anchor "
                    f"{anchor_id!r}; use lowercase ASCII letters, digits, hyphens, and underscores"
                )
            if counts[anchor_id] > 1:
                errors.append(
                    f"{path.relative_to(ROOT)}:{line_number}: duplicate HTML anchor {anchor_id!r}"
                )

    english_pages = [
        path for path in markdown if not path.is_symlink() and not is_chinese_page(path)
    ]
    for english in english_pages:
        chinese = paired_markdown(english)
        if not chinese.exists():
            continue
        english_ids = {anchor_id for _line, anchor_id in english_section_ids(english)}
        chinese_ids = {anchor_id for _line, anchor_id in explicit_anchor_ids(chinese)}
        for missing in sorted(english_ids - chinese_ids):
            errors.append(
                f"{chinese.relative_to(ROOT)}: missing explicit English section anchor "
                f"{missing!r} from {english.relative_to(ROOT)}"
            )
    return errors


def check_chinese_internal_links(files: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    for source in markdown_paths(files):
        if source.is_symlink() or not is_chinese_page(source):
            continue
        english_switch = paired_markdown(source).resolve()
        for line, raw_target in link_targets(source.read_text(encoding="utf-8")):
            target, _fragment = resolve_local_target(source, raw_target)
            if target is None or not target.exists() or target.is_dir():
                continue
            if target.suffix.lower() not in MARKDOWN_SUFFIXES or is_chinese_page(target):
                continue
            chinese_target = paired_markdown(target)
            if not chinese_target.exists():
                continue
            if line <= LANGUAGE_SWITCH_LINES and target.resolve() == english_switch:
                continue
            errors.append(
                f"{source.relative_to(ROOT)}:{line}: Chinese page links English target "
                f"{raw_target!r}; use {chinese_target.relative_to(ROOT)}"
            )
    return errors


def check_forbidden_repositories(files: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    for path in markdown_paths(files):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if OLD_MCP_REPOSITORY.search(line):
                errors.append(
                    f"{path.relative_to(ROOT)}:{line_number}: references retired MCP repository; "
                    "use WU-CVGL/determined_cluster_mcp"
                )
    return errors


def unique_markdown_files(files: Iterable[Path]) -> list[Path]:
    """Return one Markdown source per real file, preferring non-symlink pages."""

    markdown = markdown_paths(files)
    selected: dict[Path, Path] = {}
    for path in sorted(markdown, key=lambda item: (item.is_symlink(), str(item))):
        selected.setdefault(path.resolve(), path)
    return sorted(selected.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    files = repository_files()
    markdown = unique_markdown_files(files)
    errors = check_symlinks(files)
    errors.extend(check_markdown(markdown))
    errors.extend(check_language_pairs(files))
    errors.extend(check_readme_aliases())
    errors.extend(check_language_switches(files))
    errors.extend(check_stable_section_anchors(files))
    errors.extend(check_chinese_internal_links(files))
    errors.extend(check_forbidden_repositories(files))
    errors.extend(check_structured_files(files))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"documentation checks failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        f"documentation checks passed: {len(markdown)} Markdown files, "
        "local links/anchors and JSON/YAML syntax verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
