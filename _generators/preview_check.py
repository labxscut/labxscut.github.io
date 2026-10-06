#!/usr/bin/env python3
"""Structural QA on the rendered preview (_preview/): no unrendered Liquid,
expected content present, no broken in-site links."""
from __future__ import annotations

import re
import sys
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get(
    "LABX_PREVIEW_DIR",
    str(Path(tempfile.gettempdir()) / "labxscut-site-preview"),
))

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    print(("ok   " if condition else "FAIL ") + message)
    if not condition:
        failures.append(message)


pages = {str(p.relative_to(OUT)).replace("\\", "/"): p.read_text(encoding="utf-8") for p in OUT.rglob("*.html")}
check(len(pages) >= 40, f"rendered {len(pages)} html files")

leftovers = {name: len(re.findall(r"\{\{|\{%", text)) for name, text in pages.items()}
leftovers = {k: v for k, v in leftovers.items() if v}
check(not leftovers, f"no unrendered Liquid (offenders: {leftovers})")

index = pages["index.html"]
check("Machine learning for" in index, "home: hero headline")
check(index.count('class="project') >= 3, "home: tool cards")
check(index.count('class="card') >= 4, "home: research cards")
check("sxSNF" in index and "sxLaep" in index and "DeepLB" in index, "home: lists all three tools")
check("Xia Li" in index and "夏立" in index, "home: PI named")

tools = pages["tools/index.html"]
for name, url in (("sxLaep", "https://labxscut.github.io/sxLaep/"),
                  ("DeepLB", "https://labxscut.github.io/deeplb/"),
                  ("sxSNF", "https://labxscut.github.io/sxSNF/")):
    check(url in tools, f"tools: {name} docs link {url}")

people = pages["people/index.html"]
for section in ("Principal investigator", "PhD students", "Master's students",
                "Undergraduate researchers", "Alumni and collaborators"):
    check(section in people, f"people: section '{section}'")
check('/lcx/' in people and '/dhy/' in people, "people: member page links")
check(not re.search(r"@scut\.edu\.cn|\.qq\.com|\b1[3-9]\d{9}\b", people), "people: no personal contact data leaked")

pubs = pages["publications/index.html"]
check(pubs.count('class="pub"') >= 30, f"publications: {pubs.count('class=\"pub\"')} entries")
check("10.1109/TCBBIO.2026.3697777" in pubs, "publications: sxSNF DOI present")

resources = pages["resources/index.html"]
check("Wushan" in resources, "resources: postal address")
check("/assets/img/scut-logo.png" in resources, "resources: logo asset referenced")

person = pages["dhy/index.html"]
check("Duan Hongyu" in person and "段宏宇" in person, "person page: dhy identity")
check("sxSNF" in person, "person page: dhy tool link")

# in-site links must resolve inside the preview
missing: list[str] = []
for name, text in pages.items():
    for href in re.findall(r'href="(/[^"#]*)"', text):
        if href.startswith("//"):
            continue
        target = OUT / href.strip("/")
        if href.endswith("/") or not target.suffix:
            candidate = target / "index.html"
        else:
            candidate = target
        if not candidate.exists():
            missing.append(f"{name} -> {href}")
check(not missing, f"all in-site links resolve ({len(set(missing))} bad: {sorted(set(missing))[:6]})")

print()
print("FAILURES:", len(failures))
sys.exit(1 if failures else 0)
