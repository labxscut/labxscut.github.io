#!/usr/bin/env python3
"""Quick QA on the generated site data (author matching, page counts, gaps)."""
from __future__ import annotations

from pathlib import Path

import yaml

from gen_publications import REPO

data = Path(REPO) / "_data"
people = yaml.safe_load((data / "people.yml").read_text(encoding="utf-8")) or []
pubs = yaml.safe_load((data / "publications.yml").read_text(encoding="utf-8")) or []
tools = yaml.safe_load((data / "tools.yml").read_text(encoding="utf-8")) or []

sections: dict[str, int] = {}
for person in people:
    sections[person["section"]] = sections.get(person["section"], 0) + 1

pages = sorted(
    p.parent.name
    for p in (Path(REPO) / "team").glob("*/index.md")
    if "layout: profile" in p.read_text(encoding="utf-8")
)
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
print("nested profiles:", ", ".join(pages))
print(f"pubs with >=1 linked lab author: {len(matched)}/{len(pubs)}")
print("pubs with repo:", sum(1 for p in pubs if p.get("repo")), "with doi:", sum(1 for p in pubs if p.get("doi")))
print("pubs missing year:", sum(1 for p in pubs if not p.get("year")))
pub_slugs = {paper["slug"] for paper in pubs}
# Registry folders that are not (yet) rendered on the site: preprints, meeting
# abstracts and theses.  Tools may already cite them; they simply do not render
# a link until the record is promoted to a public status.
from gen_publications import PAPERS  # noqa: E402

registry_slugs = {folder.name for folder in PAPERS.iterdir() if (folder / "publication.yaml").is_file()}
registry_only = registry_slugs - pub_slugs
tool_papers = {
    (tool["key"], slug)
    for tool in tools
    for slug in (tool.get("papers") or [])
}
missing_papers = sorted(slug for _, slug in tool_papers if slug not in pub_slugs and slug not in registry_slugs)
pending_papers = sorted({slug for _, slug in tool_papers if slug in registry_only})
tool_keys = {tool["key"] for tool in tools}
missing_tools = sorted(
    (paper["slug"], key)
    for paper in pubs
    for key in (paper.get("tools") or [])
    if key not in tool_keys
)
print("invalid tool-to-publication links:", missing_papers)
print("invalid publication-to-tool links:", missing_tools)
print("tool papers pending promotion (registry only):", sorted(pending_papers))
if missing_papers or missing_tools:
    raise ValueError("tool/publication cross-references must resolve in both directions")
print("unmatched author names (no roster hit, no affiliation):", len(unmatched_authors))
for name in unmatched_authors[:25]:
    print("   -", name)
print("sample person:", pages[0], "->", next(p for p in people if p["nick"] == pages[0]))
