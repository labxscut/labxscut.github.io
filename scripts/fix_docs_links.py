#!/usr/bin/env python3
"""Unwrap local anchors in docs/site whose target does not exist in the tree.

pydoc-generated pages link to stdlib modules and to a package index page that
were never shipped, so those links are dead on the published site. Removing the
anchor while keeping its text preserves readability and lets the website sync
pass its link validation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ANCHOR = re.compile(
    r'(?is)<a\b(?P<attrs>[^>]*?href="(?P<href>[^"]*)"[^>]*?)>(?P<inner>.*?)</a>'
)
REPOS = ("sxLaep", "sxSNF", "DeepLB")
ROOT = Path(r"D:\work\labxscut")


def target_exists(page: Path, root: Path, href: str) -> bool:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or href.startswith("//") or href.startswith("#"):
        return True  # external or in-page: not our problem
    path = unquote(parsed.path)
    if not path:
        return True
    if path.startswith("/"):
        # Root-relative links are validated against the published tool route;
        # leave them for the sync script to judge.
        return True
    base = (page.parent / path).resolve()
    if base.is_file():
        return True
    if base.is_dir() or path.endswith("/"):
        return (base / "index.html").is_file()
    return False


def fix_repo(repo: Path) -> int:
    root = repo / "docs" / "site"
    if not root.is_dir():
        print(f"  {repo.name}: no docs/site, skipped")
        return 0
    changed = 0
    removed = 0
    for page in sorted(root.rglob("*.html")):
        text = page.read_text(encoding="utf-8")

        def repl(match: re.Match[str]) -> str:
            nonlocal removed
            if target_exists(page, root, match.group("href")):
                return match.group(0)
            removed += 1
            return match.group("inner")

        new = ANCHOR.sub(repl, text)
        if new != text:
            page.write_text(new, encoding="utf-8")
            changed += 1
    print(f"  {repo.name}: {changed} files rewritten, {removed} dead anchors removed")
    return changed


def main() -> int:
    if len(sys.argv) > 1:
        targets = [Path(a) for a in sys.argv[1:]]
    else:
        targets = [ROOT / name for name in REPOS]
    for repo in targets:
        fix_repo(repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
