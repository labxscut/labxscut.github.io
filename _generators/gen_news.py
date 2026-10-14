#!/usr/bin/env python3
"""Build the human-editable news feed into _data/news.yml.

The site news feed has three kinds of entry, each owned by exactly one writer
so the two generators never clobber each other (both run in the loop, in any
order, and are idempotent):

  * ``source: labxManage/Paper/<slug>``  — managed by
    agents/skills/labx-manage-sync/labxmanage_news_aggregate.py (labx_admin).
    This script preserves them untouched.
  * ``source: news/<stem>``              — owned by THIS script, generated from
    one markdown file per item under ``_news/``. This is the human-editable
    front end for announcements that are not registry papers: releases, talks,
    awards, milestones, with optional attachments.
  * no ``source`` key                    — a legacy inline entry. Preserved by
    both writers, but new items should go in ``_news/`` instead of editing the
    YAML by hand (fragile indentation, one giant file).

Each ``_news/<stem>.md`` is YAML front matter plus free prose. Only the front
matter is read; the body is there so the file is self-documenting to a human
reader and diffs cleanly per item.

Front matter keys:
  date     (required) any precision; canonicalised to YYYYMMDDHHMMSS, displayed
                     as YYYYMMDD (see the site date convention).
  text     (required) the one-line card headline. Plain text: the card and the
                     home list render it literally, so markdown link syntax
                     would show up as raw brackets. Put the link in `url`.
  url      (optional) a single link for the headline (DOI, docs page, ...).
  image    (optional) site path to an attachment thumbnail, e.g.
                     /images/news/award-2026.png. The file lives in the repo
                     under images/news/; the card shows it when present.
  alt      (optional) alt text for `image` (defaults to `text`).
  attachments (optional) list of {label, url} downloadable links (posters,
                     notices, scans). Rendered as links on the /news/ card.

Usage:  python3 _generators/gen_news.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from gen_publications import REPO, canonical_date, display_date

NEWS_DIR = REPO / "_news"
OUT = REPO / "_data" / "news.yml"
IMAGE_DIR = REPO / "images" / "news"

SOURCE_PREFIX = "news/"


def is_managed(source: str) -> bool:
    """An entry owned by the labxManage aggregator — never rewritten here."""
    return str(source or "").startswith("labxManage/")


def is_ours(source: str) -> bool:
    return str(source or "").startswith(SOURCE_PREFIX)


def parse_item(path: Path) -> dict | None:
    """Front matter of one _news file -> a news.yml entry, or None if invalid.

    A bad item is skipped with a warning rather than dropping the whole feed,
    mirroring the aggregator's per-record WARN behaviour.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        print(f"WARN: {path.name}: no front matter, skipped", file=sys.stderr)
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        print(f"WARN: {path.name}: unterminated front matter, skipped", file=sys.stderr)
        return None
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        print(f"WARN: {path.name}: front matter parse failed ({exc})", file=sys.stderr)
        return None
    if not isinstance(fm, dict):
        print(f"WARN: {path.name}: front matter is not a mapping, skipped", file=sys.stderr)
        return None

    headline = str(fm.get("text") or "").strip()
    if not headline:
        print(f"WARN: {path.name}: empty `text`, skipped", file=sys.stderr)
        return None
    canon = canonical_date(fm.get("date"))
    if not canon:
        print(f"WARN: {path.name}: unreadable `date` ({fm.get('date')!r}), skipped",
              file=sys.stderr)
        return None

    entry = {
        "date": canon,
        "date_display": display_date(canon),
        "text": headline,
        "source": f"{SOURCE_PREFIX}{path.stem}",
    }
    url = str(fm.get("url") or "").strip()
    if url:
        entry["url"] = url
    image = str(fm.get("image") or "").strip()
    if image:
        # Normalise to a site-absolute path and warn (do not fail) if the file
        # is missing, so a typo shows up in the loop instead of a broken image.
        if not image.startswith("/"):
            image = "/" + image
        entry["image"] = image
        rel = image.lstrip("/")
        if not (REPO / rel).is_file():
            print(f"WARN: {path.name}: image {image!r} not found under the repo",
                  file=sys.stderr)
        entry["alt"] = str(fm.get("alt") or headline)

    # attachments: list of {label, url}. Kept only when each has a url, so a
    # half-filled entry cannot render an empty link.
    raw_att = fm.get("attachments")
    if isinstance(raw_att, list):
        atts = []
        for a in raw_att:
            if not isinstance(a, dict):
                continue
            url = str(a.get("url") or "").strip()
            if not url:
                continue
            atts.append({"label": str(a.get("label") or "Attachment").strip(),
                         "url": url})
        if atts:
            entry["attachments"] = atts
    return entry


def collect() -> list[dict]:
    if not NEWS_DIR.is_dir():
        return []
    entries = []
    for path in sorted(NEWS_DIR.glob("*.md")):
        if path.name.startswith(("_", ".")) or path.name.lower() == "readme.md":
            continue
        entry = parse_item(path)
        if entry:
            entries.append(entry)
    return entries


# Keep byte-identical to HEADER in
# agents/skills/labx-manage-sync/labxmanage_news_aggregate.py: both writers emit
# it, so a divergence would make each --write churn the file and the two runs
# would never settle.
HEADER = (
    "# Site news feed. Three kinds of entry, each owned by one writer:\n"
    "#   source: labxManage/...  managed by\n"
    "#     agents/skills/labx-manage-sync/labxmanage_news_aggregate.py (labx_admin).\n"
    "#   source: news/...        generated by _generators/gen_news.py from _news/*.md\n"
    "#     (the human-editable front end: one markdown file per announcement).\n"
    "#   (no source)             legacy inline entry; add new items under _news/.\n"
    "# Paper entries are PI-led only: collaborative papers are not announced here\n"
    "# (the gate reads pi_track from _data/publications.yml). Edit the labxManage\n"
    "# record or the _news/ file, not this generated file.\n"
    "# Date convention: `date` is canonical YYYYMMDDHHMMSS (sorting/logic only);\n"
    "# `date_display` is the YYYYMMDD shown on the site.\n"
)


def merge(existing: list, ours: list[dict]) -> tuple[list, list[str]]:
    """Replace our news/* entries with the regenerated set; keep the rest.

    Run-order independent, and it migrates the fragile inline feed:

      * A ``_news`` item whose URL matches a **managed** (``labxManage/``) entry
        yields — the aggregator owns registry papers, so the two writers running
        in either order never show a paper twice.
      * A **legacy** entry (no ``source``) whose URL matches a ``_news`` item is
        dropped: the markdown file is the durable home for that announcement, so
        adding ``_news/x.md`` retires the hand-written inline row in the same
        run, and the result is idempotent (re-running changes nothing).
    """
    ours_urls = {str(e.get("url") or "") for e in ours if e.get("url")}

    kept: list[dict] = []
    managed_urls: set[str] = set()
    for e in existing:
        if is_ours(e.get("source")):
            continue  # regenerated below
        if is_managed(e.get("source")):
            if e.get("url"):
                managed_urls.add(str(e["url"]))
            kept.append(e)
        elif e.get("url") and str(e["url"]) in ours_urls:
            # legacy inline row being migrated to a _news file
            continue
        else:
            kept.append(e)

    ours_kept: list[dict] = []
    yielded: list[str] = []
    for e in ours:
        if e.get("url") and str(e["url"]) in managed_urls:
            yielded.append(f"{e['source']} (managed entry owns {e['url']})")
            continue
        ours_kept.append(e)

    old_ours = {str(e.get("source")) for e in existing if is_ours(e.get("source"))}
    new_ours = {e["source"] for e in ours_kept}
    log = [f"add    {s}" for s in sorted(new_ours - old_ours)]
    log += [f"remove {s}" for s in sorted(old_ours - new_ours)]
    log += [f"yield  {s}" for s in yielded]
    merged = kept + ours_kept
    merged.sort(key=lambda e: (str(e.get("date") or ""), str(e.get("source") or "")),
                reverse=True)
    return merged, log


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="print changes without writing")
    ap.add_argument("--write", action="store_true", help="write merged news.yml")
    args = ap.parse_args()
    if not args.dry_run and not args.write:
        args.dry_run = True

    ours = collect()
    existing: list = []
    if OUT.is_file():
        loaded = yaml.safe_load(OUT.read_text(encoding="utf-8")) or []
        if isinstance(loaded, list):
            existing = loaded

    merged, log = merge(existing, ours)

    print(f"_news items: {len(ours)}")
    print(f"managed (labxManage) kept: {len([e for e in merged if is_managed(e.get('source'))])}")
    print(f"legacy inline kept: "
          f"{len([e for e in merged if not e.get('source')])}")
    for line in log:
        print("  ", line)
    if not log:
        print("   (no changes)")

    if args.write:
        body = yaml.safe_dump(merged, allow_unicode=True, sort_keys=False, width=100)
        OUT.write_text(HEADER + body, encoding="utf-8")
        print(f"wrote {OUT}")
    else:
        print("dry-run only; re-run with --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
