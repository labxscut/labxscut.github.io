#!/usr/bin/env python3
"""Quick QA on the generated site data (author matching, page counts, gaps).

Offline by default. Pass ``--check-repos`` to also verify that every catalogued
tool's repository is publicly reachable, because ``_data/tools.yml`` renders its
``repo``/``docs`` links on the public /tools/ page and a private repo 404s for
every visitor. Add ``--strict`` to make that check fail the run.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

from gen_publications import REPO

# Ceiling on authors that fall back to the raw registry string, enforced by
# --strict. Set from the verified state after the first full harvest (13 names,
# all inside two records that genuinely cannot align: XiaBB2015 has a registry
# typo "Fuhrmann" vs the publisher's "Fuhrman", SunJCO2020 has "TF Sun" vs
# "Thomas Yang Sun"). Raising it requires re-running the harvester and
# confirming each new fallback is a real non-alignment, not a regression.
REGISTRY_FALLBACK_BUDGET = 13

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


def audit_css_variables() -> list[str]:
    """Report every var(--x) that no stylesheet or template defines.

    An undefined custom property is a silent failure: Sass compiles it happily,
    Jekyll builds, and the declaration simply behaves as if absent (or, for a
    non-inherited property, as `unset`). Three real defects of this class were
    found by hand -- --text-color-secondary (muted text rendered at full body
    colour), --theme-light (<details> panels rendered transparent) and --white.

    Definitions are collected from _styles/*.scss and also from _includes/ and
    _layouts/, because templates set some variables inline (content.html emits
    style="--image: url(...)" per section).
    """
    defined: set[str] = set()
    used: dict[str, list[str]] = {}
    roots = [
        (Path(REPO) / "_styles", "*.scss"),
        (Path(REPO) / "_includes", "*.html"),
        (Path(REPO) / "_layouts", "*.html"),
    ]
    for folder, pattern in roots:
        for path in sorted(folder.glob(pattern)):
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(REPO).as_posix()
            # Strip comments first: an explanatory comment that mentions a
            # removed variable must not count as a use (or as a definition).
            text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
            # (?<!:) keeps `https://` inside url() from being read as a comment.
            text = re.sub(r"(?<!:)//[^\n]*", " ", text)
            text = re.sub(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", " ", text, flags=re.S)
            text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
            for name in re.findall(r"(--[a-zA-Z0-9-]+)\s*:", text):
                defined.add(name)
            for name in re.findall(r"var\(\s*(--[a-zA-Z0-9-]+)", text):
                used.setdefault(name, []).append(rel)
    undefined = sorted(name for name in used if name not in defined)
    for name in undefined:
        sites = ", ".join(sorted(set(used[name]))[:4])
        print(f"   UNDEFINED {name} used in {sites}")
    print(f"css variables: {len(used)} used, {len(defined)} defined, {len(undefined)} undefined")
    return undefined


print()
undefined_css_vars = audit_css_variables()
if undefined_css_vars and "--strict" in sys.argv:
    raise ValueError(
        "every var(--x) must be defined in _styles/ or set inline by a template; "
        f"undefined: {undefined_css_vars}"
    )



def audit_author_names() -> tuple[list[str], int]:
    """Enforce the canonical author-name transform on every generated record.

    Publisher imports MUST pass through the shared name transform
    (agents/hermes/lib/author_name.py, SOP: agents/sop/labxscut-backend-specs.md
    § Author names). This is the gate that makes "must" mean something: an
    import that skips the transform, or a generator edit that bypasses
    ``canonical_author``, leaves a name here in the untransformed registry shape
    and fails the run instead of silently shipping "DM Ai" next to "Dongmei Ai"
    for the same person.

    Three things are checked, and the distinctions matter:

    * ``name_source`` must be present on every author. It is the audit trail for
      which evidence won (roster / publisher / registry), so a record without it
      means the transform never ran.
    * A name that DID resolve (roster or publisher) must have canonical SHAPE:
      every token is either a word or a dotted single letter, with no all-caps
      abbreviation run, no bracket and no doubled space. Shape is tested rather
      than re-rendered, because re-splitting "Dongmei Ai" into surname+given is
      genuinely ambiguous -- both tokens are surname candidates -- so a
      round-trip check would false-positive on every ordinary two-word name.
    * ``registry`` names are the documented fallback: the record had no usable
      DOI, or the publisher list would not align positionally with the registry
      list, so there is no fuller evidence to prefer and the registry string is
      kept verbatim (backlog 3.20's own fallback). Those are COUNTED, not
      failed -- 13 today, all in two records that genuinely cannot align. A jump
      in that count means the harvester regressed, so --strict gates it.
    """
    problems: list[str] = []
    fallbacks = 0
    # An all-caps run of 2+ letters is the untransformed registry shape ("DM",
    # "LC"). A bare single letter with no dot is an initial that lost its dot.
    caps_run = re.compile(r"(?<![A-Za-z])[A-Z]{2,}(?![A-Za-z])")
    bracket = re.compile(r"[\(\)\[\]\{\}]")
    for rel, records in (("_data/publications.yml", pubs), ("_data/abstracts.yml", abstracts)):
        for paper in records:
            slug = paper.get("slug") or "?"
            for i, a in enumerate(paper.get("authors") or []):
                name = str(a.get("name") or "")
                source = str(a.get("name_source") or "")
                if not source:
                    problems.append(f"{rel} {slug}[{i}] {name!r}: no name_source "
                                    "(the canonical transform never ran)")
                    continue
                if source == "registry":
                    fallbacks += 1
                    continue
                why = ""
                if not name.strip():
                    why = "empty name"
                elif bracket.search(name):
                    why = f"bracket left in the name: {bracket.search(name).group()!r}"
                elif name != " ".join(name.split()):
                    why = "doubled or leading/trailing space"
                elif caps_run.search(name):
                    why = f"all-caps abbreviation run {caps_run.search(name).group()!r}"
                else:
                    for tok in name.split():
                        core = tok.strip(".")
                        if len(core) == 1 and not core.isalpha():
                            why = f"non-letter token {tok!r}"
                            break
                        if len(core) == 1 and not tok.endswith("."):
                            why = f"undotted initial {tok!r}"
                            break
                if why:
                    problems.append(f"{rel} {slug}[{i}] {name!r}: {why} ({source})")
    for p in problems[:30]:
        print("   NONCANONICAL", p)
    if len(problems) > 30:
        print(f"   ... and {len(problems) - 30} more")
    print(f"author names: {len(problems)} non-canonical, {fallbacks} registry fallbacks")
    return problems, fallbacks


print()
name_problems, name_fallbacks = audit_author_names()
if "--strict" in sys.argv:
    if name_problems:
        raise ValueError(
            "every author name that resolved from the roster or a publisher "
            "harvest must be in canonical `First M. Last` form; run "
            "_generators/harvest_author_names.py and regenerate. Offenders: "
            + "; ".join(name_problems[:5])
        )
    if name_fallbacks > REGISTRY_FALLBACK_BUDGET:
        raise ValueError(
            f"{name_fallbacks} authors fell back to the raw registry string, "
            f"above the budget of {REGISTRY_FALLBACK_BUDGET}. The fallback is "
            "legitimate only when a record has no usable DOI or its publisher "
            "list will not align; a jump means the harvester regressed. Run "
            "_generators/harvest_author_names.py --dry-run to see why."
        )


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
