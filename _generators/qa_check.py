#!/usr/bin/env python3
"""Quick QA on the generated site data (author matching, page counts, gaps).

Offline by default. Pass ``--check-repos`` to also verify that every catalogued
tool's repository is publicly reachable, because ``_data/tools.yml`` renders its
``repo``/``docs`` links on the public /tools/ page and a private repo 404s for
every visitor. Add ``--strict`` to make that check fail the run.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from gen_publications import REPO

data = Path(REPO) / "_data"
people = yaml.safe_load((data / "people.yml").read_text(encoding="utf-8")) or []
pubs = yaml.safe_load((data / "publications.yml").read_text(encoding="utf-8")) or []
abstracts = yaml.safe_load((data / "abstracts.yml").read_text(encoding="utf-8")) or []
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
# An author nick that is not in people.yml renders as plain text (correct for a
# roster row marked hide:true), but it also inflates the "linked lab author"
# count, so surface it instead of leaving it silent.
people_nicks = {p["nick"] for p in people}
dangling_nicks = sorted(
    {
        (a["nick"], paper["slug"])
        for paper in pubs + abstracts
        for a in (paper.get("authors") or [])
        if a.get("nick") and a["nick"] not in people_nicks
    }
)
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
if dangling_nicks:
    print(f"author nicks not in people.yml (render as plain text, inflate the count above): {len(dangling_nicks)}")
    for nick, slug in dangling_nicks:
        print(f"   - {nick} in {slug}")
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


def public_repo_status(url: str) -> tuple[str, str]:
    """Reachability of a GitHub repo URL as ('public'|'private'|'skip', name).

    Uses the authenticated ``gh`` CLI: an unauthenticated probe is rate-limited
    to 60 requests/hour and a flaky network returns no status at all, so an
    anonymous curl cannot tell "private" from "rate-limited" and would report
    false positives. ``gh`` answers ``private`` only on a definitive 404 and
    ``skip`` on any transport/rate-limit failure, which is never treated as a
    defect.
    """
    name = (url or "").rstrip("/").split("github.com/")[-1]
    if not name or "/" not in name:
        return "skip", f"not a github.com repo URL: {url!r}"
    try:
        proc = subprocess.run(
            ["gh", "api", f"repos/{name}", "--jq", ".private"],
            capture_output=True, text=True, timeout=60,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (OSError, subprocess.TimeoutExpired):
        return "skip", name
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "")
    if proc.returncode == 0 and out == "false":
        return "public", name
    if proc.returncode == 0 and out == "true":
        return "private", name
    # 404 on an authenticated call means the repo is private or gone: both are
    # invisible to a site visitor, which is the condition we care about.
    if "404" in err or "Could not resolve to a Repository" in err:
        return "private", name
    return "skip", name


if "--check-repos" in sys.argv:
    print()
    print("catalogued tool repositories (visibility):")
    private = []
    skipped = []
    declared = []
    reachable = []
    for tool in tools:
        # `private: true` is the catalog's own declaration that the repository is
        # not public, so the templates suppress its links. Report it as declared,
        # not as a defect — but still verify the declaration is true, because a
        # stale flag would hide a link that could be shown.
        is_declared = bool(tool.get("private"))
        for field in ("repo", "docs"):
            url = str(tool.get(field) or "")
            if "github.com/" not in url:
                continue  # a hosted docs site, not a repo — out of scope here
            status, name = public_repo_status(url)
            if status == "private":
                (declared if is_declared else private).append((tool["key"], field, name))
            elif status == "skip":
                skipped.append((tool["key"], field, name))
            elif is_declared:
                print(f"      STALE FLAG: {tool['key']}.{field} = github.com/{name} "
                      f"is public but tools.yml says private: true")
            else:
                reachable.append((tool["key"], field, name))
        # Extra repositories (e.g. a review paper's benchmark companion) are
        # always linked, so they must always be public — `private: true` does not
        # excuse them.
        for extra in (tool.get("benchmarks") or []):
            url = str(extra.get("url") or "")
            if "github.com/" not in url:
                continue
            label = f"benchmarks[{extra.get('label') or '?'}]"
            status, name = public_repo_status(url)
            if status == "private":
                private.append((tool["key"], label, name))
            elif status == "skip":
                skipped.append((tool["key"], label, name))
            else:
                reachable.append((tool["key"], label, name))
    if declared:
        print(f"   private as declared in tools.yml (links suppressed on site): {len(declared)}")
        for key, field, name in declared:
            print(f"      {key}.{field} = github.com/{name}")
    if private:
        print(f"   NOT publicly reachable and NOT declared: {len(private)} link(s)")
        for key, field, name in private:
            print(f"      {key}.{field} = github.com/{name} — /tools/ shows a dead link")
        if "--strict" in sys.argv:
            raise ValueError(
                "catalogued tools must link publicly reachable repositories; "
                "make the repo public, drop the catalog entry, or mark it "
                "`private: true` so the templates suppress the link"
            )
    # List what WAS verified so a silent section can never be mistaken for a pass
    # (e.g. a renamed `benchmarks` field would otherwise check nothing at all).
    print(f"   publicly reachable: {len(reachable)}")
    for key, field, name in reachable:
        print(f"      {key}.{field} = github.com/{name}")
    if not private and not skipped:
        print("   every catalogued repo/docs/benchmark link is publicly reachable")
    if skipped:
        print(f"   could not verify (network/rate limit, not a defect): {len(skipped)}")
        for key, field, name in skipped:
            print(f"      {key}.{field} = {name}")
