#!/usr/bin/env python3
"""Build _data/publications.yml from the labxManage paper records.

Source of truth: ~/work/advisee/hc/labxManage/Paper/<slug>/publication.yaml
(Feishu "LabxManageHermes" mirror; do not hand-edit those files from here).

Only records that are safe to publish go into the site:
  status in {Published, Final, Accept, Accepted}  AND a real title
  AND the venue is known. WIP / ToSub / UdRev / TPL records stay private.
Duplicate source records are collapsed by DOI or normalized title and venue.

Usage (WSL):  python3 _generators/gen_publications.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import yaml

WORK = Path(os.environ.get("LABX_WORK", "/mnt/d/work"))
REPO = WORK / "labxscut" / "labxscut.github.io"
PAPERS = WORK / "advisee" / "hc" / "labxManage" / "Paper"
CONTACT = WORK / "advisee" / "core" / "database" / "contact.md"
OUT = REPO / "_data" / "publications.yml"

PUBLIC_STATUS = {"Published", "Final", "Accept", "Accepted"}


def load_roster() -> list[dict]:
    """Parse the roster markdown table into rows (nick, names, github)."""
    rows: list[dict] = []
    for line in CONTACT.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 14 or cells[0] in {"Nick", "----"} or set(cells[0]) <= {"-"}:
            continue
        if cells[0] in {"lab", "xyz"}:
            continue
        nick, group, degree, year, status = cells[0], cells[1], cells[2], cells[3], cells[4]
        affiliation, name_en, name_zh, note = cells[5], cells[6], cells[7], cells[13]
        gh = re.search(r"https://github\.com/([A-Za-z0-9_.-]+)", note)
        rows.append(
            {
                "nick": nick,
                "group": group,
                "degree": degree,
                "year": year,
                "status": status,
                "affiliation": affiliation,
                "name_en": name_en,
                "name_zh": name_zh,
                "github": gh.group(1) if gh else "",
                # Optional note markers curated in the roster:
                #   Type=<label>   relationship label (Collaborator, VisitingScholar, ...)
                #   Site=false     hide the public labxscut.github.io page
                #   Alumni=true    list under Alumni while still collaborating
                #   Now=<text>     current position shown on the public profile
                "type": match_note_marker(note, "Type"),
                "site": "false" if match_note_marker(note, "Site") == "false" else "",
                "alumni": match_note_marker(note, "Alumni") == "true",
                "now": match_note_marker(note, "Now"),
            }
        )
    return rows


def match_note_marker(note: str, key: str) -> str:
    """Return the value of a ``Key=value`` marker embedded in a roster note.

    Markers are ``; ``-separated, so the value may contain spaces as long as it
    does not contain a semicolon.
    """
    match = re.search(rf"\b{key}=(.*?)(?:\s*;\s*|\s*$)", note or "")
    return match.group(1).strip() if match else ""


def roster_lookup(rows: list[dict]) -> dict[str, dict]:
    """Index roster rows by a normalized name key and by Chinese name.

    The roster writes names surname-first ("Duan Hongyu") while the paper
    records write them given-first ("Hongyu Duan"), so compare sorted token
    sets with single-letter initials dropped ("Li C. Xia" == "Xia Li").
    """
    index: dict[str, dict] = {}
    for row in rows:
        key = name_key(row["name_en"])
        if key:
            index.setdefault(key, row)
        if row["name_zh"]:
            index.setdefault(row["name_zh"].strip(), row)
    return index


def name_key(name: str) -> str:
    tokens = [t for t in re.findall(r"[A-Za-z]+", (name or "").lower()) if len(t) > 1]
    return " ".join(sorted(tokens))


def lookup_author(name_en: str, name_zh: str, lookup: dict[str, dict]) -> dict | None:
    row = lookup.get(name_key(name_en))
    if not row and name_zh:
        row = lookup.get(name_zh.strip())
    return row


def clean(value) -> str:
    return str(value).strip() if value is not None else ""


def read_record(path: Path) -> dict:
    """Load a publication.yaml, tolerating the Feishu placeholders (source: ??)."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^(\s*source:\s*)\?+\s*$", r'\1"?"', text)
    return yaml.safe_load(text) or {}


def pi_track(entry: dict, cv_index: dict[str, str] | None = None) -> str:
    """Which CV section a paper belongs to: PI-led, collaborative, or a chapter.

    Mirrors the CV layout (Research Articles / Collaborative Articles / Book
    Chapters). Order of authority: an explicit category on the record, then the
    CV's own sectioning, then the author roles (first or corresponding author
    means PI-led).
    """
    if entry.get("venue_type") == "book" or entry.get("category") == "book-chapter":
        return "book-chapter"
    if entry.get("category") in {"research", "collaborative"}:
        # The CV already files these under Research / Collaborative articles.
        return "lead" if entry["category"] == "research" else "collaborative"
    doi = clean(entry.get("doi")).lower()
    if cv_index:
        track = cv_index.get(f"doi:{doi}") or cv_index.get(f"title:{normalize(clean(entry.get('title')))}")
        if track:
            return track
    names = [str(a.get("name") or "").lower().rstrip(".").strip() for a in entry.get("authors") or []]
    roles = {
        str(a.get("role") or "")
        for a, n in zip(entry.get("authors") or [], names)
        if n.endswith("xia") or n in {"lc xia", "li c. xia", "li c xia"}
    }
    if "first_author" in roles or "corresponding_author" in roles:
        return "lead"
    rank, total = entry.get("xia_rank"), entry.get("n_authors")
    if isinstance(rank, int) and isinstance(total, int) and rank > 0:
        if rank == 1 or rank == total:
            return "lead"
    return "collaborative"


def build_entry(slug: str, doc: dict, lookup: dict[str, dict], cv_index: dict[str, str] | None = None) -> dict | None:
    lifecycle = doc.get("lifecycle") or {}
    status = clean(lifecycle.get("status"))
    if status not in PUBLIC_STATUS:
        return None
    # Scholar/CV backfill records opt in explicitly; abstracts, preprints and
    # theses stay in the registry only until a human promotes them.
    if doc.get("published_on_site") is False:
        return None

    title = clean(doc.get("title"))
    venue = doc.get("venue") or {}
    venue_name = clean(venue.get("full_name") or venue.get("name"))
    # Placeholder records use the folder slug as the title and carry no venue.
    if not title or title == slug or len(title) < 12 or not venue_name:
        return None

    ids = doc.get("identifiers") or {}
    metrics = doc.get("metrics") or {}
    indexing = doc.get("indexing") or {}
    authorship = doc.get("authorship") or {}

    authors: list[dict] = []
    lab_authors: list[str] = []
    for author in doc.get("authors") or []:
        name_en = clean(author.get("name_en"))
        if not name_en:
            continue
        match = lookup_author(name_en, clean(author.get("name_zh")), lookup)
        entry = {
            "name": name_en,
            "name_zh": clean(author.get("name_zh")),
            "role": clean(author.get("role")),
            "level": clean(author.get("level")),
            "affiliation": clean(author.get("affiliation")),
            "nick": match["nick"] if match else "",
        }
        authors.append(entry)
        if entry["nick"] and entry["nick"] not in lab_authors:
            lab_authors.append(entry["nick"])

    year = ""
    match = re.search(r"(20\d{2})", clean(lifecycle.get("pub_date")) or clean(lifecycle.get("decision_date")))
    if match:
        year = match.group(1)
    else:
        # Some legacy records encode only the two-digit year in their slug.
        match = re.search(r"(?<!\d)(2\d)(?!\d)", slug)
        if match:
            year = f"20{match.group(1)}"

    doi = clean(ids.get("doi"))
    if not re.match(r"^10\.\d{4,9}/\S+$", doi, re.IGNORECASE):
        doi = ""
    url = clean(ids.get("ieee_url")) or (f"https://doi.org/{doi}" if doi else "")

    entry = {
        "slug": slug,
        "title": title,
        "venue": venue_name,
        "venue_short": clean(venue.get("name")) or venue_name,
        "venue_type": clean(venue.get("type")) or "journal",
        "category": clean(doc.get("category")) or "other",
        "pi_role": clean(doc.get("role")),
        "year": year,
        "status": status,
        "doi": doi,
        "url": url,
        "repo": clean(ids.get("repo_url")),
        "if": clean(metrics.get("impact_factor")),
        "quartile": clean(metrics.get("jcr_quartile")),
        "ccf": clean(indexing.get("ccf")),
        "sci": bool(indexing.get("sci")),
        "xia_rank": authorship.get("xia_rank"),
        "n_authors": authorship.get("n_authors"),
        "authors": authors,
        "lab_authors": lab_authors,
    }
    entry["pi_track"] = pi_track(entry, cv_index)
    return entry


def publication_key(entry: dict) -> tuple[str, ...]:
    """Return a stable key for duplicate records of the same publication."""
    doi = clean(entry.get("doi")).lower()
    if doi:
        return ("doi", doi)
    title = re.sub(r"[^a-z0-9]+", "", clean(entry.get("title")).lower())
    venue = re.sub(r"[^a-z0-9]+", "", clean(entry.get("venue")).lower())
    return ("title", title, venue, clean(entry.get("year")))


def entry_quality(entry: dict) -> tuple[int, ...]:
    """Prefer records with complete author, repository, and citation metadata."""
    return (
        len(entry.get("lab_authors") or []),
        len(entry.get("authors") or []),
        bool(entry.get("repo")),
        bool(entry.get("url")),
        entry.get("status") == "Published",
        not entry.get("slug", "").startswith("Feishu-"),
    )


def deduplicate(entries: list[dict]) -> tuple[list[dict], int]:
    unique: dict[tuple[str, ...], dict] = {}
    for entry in entries:
        key = publication_key(entry)
        existing = unique.get(key)
        if existing is None or entry_quality(entry) > entry_quality(existing):
            unique[key] = entry
    result = list(unique.values())
    result.sort(key=lambda e: (e["year"] or "0", e["title"]), reverse=True)
    return result, len(entries) - len(result)


def cv_sections() -> dict[str, str]:
    """Index the CV's own publication sections by DOI and normalized title.

    The CV (``advisee/hc/0fund/00lcx-cv/LiXia.cv.en.md``) is the curated split
    between Research Articles (first/corresponding) and Collaborative Articles,
    so it decides the section for the Feishu records that carry no category.
    """
    try:
        entries = parse_cv_entries()
    except Exception:  # the CV is optional context; roles can classify without it
        return {}
    index: dict[str, str] = {}
    for entry in entries:
        value = {"research": "lead", "collaborative": "collaborative", "book-chapter": "book-chapter"}[
            entry["category"]
        ]
        if entry["doi"]:
            index[f"doi:{entry['doi'].lower()}"] = value
        index.setdefault(f"title:{normalize(entry['title'])}", value)
    return index


def parse_cv_entries() -> list[dict]:
    """Parse the CV with the backfill generator's parser (same _generators dir)."""
    import importlib.util

    path = Path(__file__).resolve().parent / "backfill_cv_papers.py"
    spec = importlib.util.spec_from_file_location("backfill_cv_papers", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_cv()


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def tools_by_paper() -> dict[str, list[str]]:
    """Read explicit tool-to-paper links from the site's tools data."""
    path = REPO / "_data" / "tools.yml"
    if not path.exists():
        return {}
    records = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    result: dict[str, list[str]] = {}
    for tool in records:
        for slug in tool.get("papers") or []:
            result.setdefault(slug, []).append(tool["key"])
    return result


def main() -> int:
    roster = load_roster()
    lookup = roster_lookup(roster)
    cv_index = cv_sections()
    paper_tools = tools_by_paper()
    entries: list[dict] = []
    skipped = 0
    for folder in sorted(p for p in PAPERS.iterdir() if p.is_dir()):
        path = folder / "publication.yaml"
        if not path.exists():
            continue
        doc = read_record(path)
        entry = build_entry(folder.name, doc, lookup, cv_index)
        if entry:
            entry["tools"] = paper_tools.get(folder.name, [])
            entries.append(entry)
        else:
            skipped += 1

    entries, duplicates = deduplicate(entries)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Generated by _generators/gen_publications.py - do not hand-edit.\n"
        "# Source: advisee/hc/labxManage/Paper/<slug>/publication.yaml (published and accepted records).\n"
    )
    OUT.write_text(
        header + yaml.safe_dump(entries, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    published = sum(1 for entry in entries if entry["status"] not in {"Accept", "Accepted"})
    accepted = len(entries) - published
    print(
        f"publications: {published} published, {accepted} accepted, "
        f"{duplicates} duplicate source records removed, {skipped} excluded"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
