#!/usr/bin/env python3
"""Quick QA on the generated site data (author matching, page counts, gaps)."""
from __future__ import annotations

from pathlib import Path

import yaml

from gen_publications import REPO

data = Path(REPO) / "_data"
people = yaml.safe_load((data / "people.yml").read_text(encoding="utf-8")) or []
pubs = yaml.safe_load((data / "publications.yml").read_text(encoding="utf-8")) or []

sections: dict[str, int] = {}
for person in people:
    sections[person["section"]] = sections.get(person["section"], 0) + 1

pages = sorted(p.stem for p in (Path(REPO) / "_people").glob("*.md"))
matched = [p for p in pubs if p.get("lab_authors")]
unmatched_authors = sorted(
    {
        a["name"]
        for p in pubs
        for a in (p.get("authors") or [])
        if not a.get("nick") and a.get("affiliation") == ""
    }
)

print("sections:", sections)
print("personal pages:", len(pages))
print(f"pubs with >=1 linked lab author: {len(matched)}/{len(pubs)}")
print("pubs with repo:", sum(1 for p in pubs if p.get("repo")), "with doi:", sum(1 for p in pubs if p.get("doi")))
print("unmatched author names (no roster hit, no affiliation):", len(unmatched_authors))
for name in unmatched_authors[:25]:
    print("   -", name)
print("sample person:", pages[0], "->", next(p for p in people if p["nick"] == pages[0]))
