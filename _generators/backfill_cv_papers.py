#!/usr/bin/env python3
"""Backfill labxManage paper records from Li C. Xia's CV.

The Feishu "LabxManageHermes" mirror under
``advisee/hc/labxManage/Paper/<slug>/publication.yaml`` only covers the recent
records, so everything published before 2022 (and both book chapters) is
missing and therefore absent from the website. The CV at
``advisee/hc/0fund/00lcx-cv/LiXia.cv.en.md`` is the curated source of truth for
those entries.

This script parses the CV publication sections and writes one record folder per
missing entry, following the existing layout (``publication.yaml`` +
``record.md`` + ``meta.json``). Existing folders are matched by DOI first and
then by normalized title, and are never overwritten - the Feishu pull stays the
authority for records it already knows about.

Usage (Git Bash / WSL / Windows Python):
    python _generators/backfill_cv_papers.py --dry-run
    python _generators/backfill_cv_papers.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import yaml

WORK = Path(os.environ.get("LABX_WORK", "/mnt/d/work"))
PAPERS = WORK / "advisee" / "hc" / "labxManage" / "Paper"
CV = WORK / "advisee" / "hc" / "0fund" / "00lcx-cv" / "LiXia.cv.en.md"

# CV subsection label -> publication category used by the site.
SECTIONS = {
    "Research Articles": "research",
    "Collaborative Articles": "collaborative",
    "Book Chapters": "book-chapter",
}

SELF = "LC Xia"
# Matches the PI's own name in any CV spelling: "LC Xia", "L. C. Xia", "Li C. Xia".
SELF_RE = re.compile(r"^l\.?\s*c\.?\s*(li\s+)?xia$|^li\s+c\.?\s*xia$", re.IGNORECASE)
DOI_RE = re.compile(r"doi:\s*\+?(10\.[0-9]{4,9}[/-][^\s,;]+)", re.IGNORECASE)
YEAR_RE = re.compile(r"\*\*(19|20)\d{2}\*\*")
VENUE_RE = re.compile(r"<u>_?([A-Za-z][^<>]*?)_?</u>")
ROLE_STAR = re.compile(r"\\\*")
NAME_TOKEN_RE = re.compile(r"^[A-Za-zÀ-ÿ'.\-+0-9]+$")


def normalize_title(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def clean_markers(text: str) -> str:
    """Drop CV bold/italic/underline markup and footnote markers."""
    text = re.sub(r"\\[*¹#]", "", text)
    text = text.replace("**", "").replace("*", "")
    text = re.sub(r"<u>|</u>|_", "", text)
    text = text.replace("¹", "").replace("^#^", "")
    return re.sub(r"\s+", " ", text).strip()


def normalize_self(text: str) -> str:
    """Spell the PI's name consistently before the author block is split.

    The CV writes it as "LC Xia", "LC. Xia" or "Li C. Xia"; the internal period
    would otherwise be read as the end of the author list.
    """
    text = re.sub(r"\bL\.?C\.?\s+Xia\b", SELF, text, flags=re.IGNORECASE)
    return re.sub(r"\bLi\s+C\.?\s*Xia\b", SELF, text, flags=re.IGNORECASE)


def parse_authors(blob: str) -> list[dict]:
    """Split a CV author block into name/role dicts.

    Roles come from the CV markup: ``\\*`` marks a (co-)corresponding author and
    ``¹`` a co-first author; the leading position is the first author.
    """
    blob = blob.replace("**", "")
    blob = normalize_self(blob)
    parts = [p.strip(" .,;") for p in re.split(r",| and | & ", blob) if p.strip(" .,;")]
    authors: list[dict] = []
    for part in parts:
        if re.match(r"^(for|in)\s", part, re.IGNORECASE):
            continue  # consortium attribution, e.g. "for Alzheimer's Disease Sequencing Project"
        starred = bool(ROLE_STAR.search(part)) or part.endswith("*")
        cofirst = "¹" in part
        name = clean_markers(part)
        name = re.sub(r"\\\*|\s+\*", "", name).strip(" *")
        if not name or not all(NAME_TOKEN_RE.match(tok) for tok in name.split()):
            continue
        if re.search(r"\bet al\b", name, re.IGNORECASE):
            name = re.sub(r"\s*\bet al\b.*$", "", name, flags=re.IGNORECASE).strip()
        authors.append(
            {
                "name_en": name,
                "starred": starred,
                "cofirst": cofirst,
            }
        )
    for index, author in enumerate(authors):
        if index == 0 or author["cofirst"]:
            author["role"] = "first_author"
        elif author["starred"]:
            author["role"] = "corresponding_author"
        else:
            author["role"] = "co_author"
        if SELF_RE.match(author["name_en"]):
            author["name_en"] = SELF
        del author["starred"]
        del author["cofirst"]
    return authors


def self_rank(authors: list[dict]) -> tuple[int, int]:
    total = len(authors)
    for index, author in enumerate(authors):
        if author["name_en"] == SELF:
            return index + 1, total
    return 0, total


def family_of(name: str) -> str:
    tokens = re.findall(r"[A-Za-z]+", name or "")
    return tokens[-1].lower() if tokens else ""


def venue_tokens(venue: str) -> set[str]:
    stop = {"of", "the", "and", "in", "on", "transactions", "proceedings", "journal"}
    return {w for w in re.findall(r"[A-Za-z]+", venue or "") if w.lower() not in stop}


def slugify(text: str, limit: int = 5) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text)
    stop = {"a", "an", "the", "of", "for", "and", "in", "on", "with", "via", "to", "from"}
    picked = [w for w in words if w.lower() not in stop][:limit]
    return "".join(w[:1].upper() + w[1:].lower() if w.isupper() else w[:1].upper() + w[1:] for w in picked)


def venue_abbr(venue: str) -> str:
    words = re.findall(r"[A-Za-z]+", venue)
    if len(words) == 1:
        return words[0][:6]
    return "".join(w[0].upper() for w in words if w.lower() not in {"of", "the", "and", "in"})[:6] or "J"


def make_slug(authors: list[dict], year: str, venue: str, title: str) -> str:
    family = re.sub(r"[^A-Za-z]", "", (authors[0]["name_en"] if authors else "Anon").split()[-1])
    family = family[:8].capitalize()
    short = slugify(title, 3)
    return f"{family}{venue_abbr(venue)}{year}{short}"[:40]


def parse_entry(line: str, category: str) -> dict | None:
    body = normalize_self(re.sub(r"^\s*\d+\.\s*", "", line).strip())
    if not body or len(body) < 20:
        return None

    doi_match = DOI_RE.search(body)
    doi = doi_match.group(1).rstrip(".,;") if doi_match else ""
    year_match = YEAR_RE.search(body)
    year = year_match.group(0).strip("*") if year_match else ""
    venue_match = VENUE_RE.search(body)
    venue = clean_markers(venue_match.group(1)) if venue_match else ""

    # Everything before the venue markup holds "authors. title."
    head = body[: venue_match.start()] if venue_match else body
    # Drop the trailing status parenthetical ("(accepted, 2025:", "(in press")
    # which the CV writes after the title and before/around the venue markup.
    if head.count("(") > head.count(")"):
        head = head[: head.rfind("(")]
    head = head.rstrip(" ,;(")
    chunks = [c for c in re.split(r"\.\s+", head) if c.strip()]
    if len(chunks) < 2:
        return None
    authors_blob = chunks[0]
    title = clean_markers(". ".join(chunks[1:]).strip(" ."))
    # Book chapters end with a dangling "In" before the book title markup.
    title = title.rstrip(" .;,")
    title = re.sub(r"(\s*\.\s*)?\bIn[\s_]*$", "", title).strip(" .;,_").strip()
    authors = parse_authors(authors_blob)
    if not authors or not title or not venue:
        return None

    rank, total = self_rank(authors)
    truncated = bool(re.search(r"\bet al\b", authors_blob, re.IGNORECASE))
    if truncated:
        # "et al" hides the real author list, so the count is unknown.
        total = 0
    role_zh = ""
    if any(a["name_en"] == SELF and a["role"] == "first_author" for a in authors):
        role_zh = "第一作者" if rank == 1 else "共同第一作者"
    if any(a["name_en"] == SELF and a["role"] == "corresponding_author" for a in authors):
        role_zh = "通讯作者" if not role_zh else role_zh + "（兼）"
    if truncated and not rank:
        role_zh = role_zh or "合著（ consortium，作者名单在 CV 中缩写为 et al）"

    status = "Final"
    if category == "book-chapter":
        venue_type = "book"
    elif category == "research" and re.search(r"accepted|in press", body, re.IGNORECASE) and not doi:
        status = "Accept"
        venue_type = "journal"
    else:
        venue_type = "journal"

    return {
        "slug": make_slug(authors, year or "0000", venue, title),
        "title": clean_markers(title),
        "venue": venue,
        "venue_type": venue_type,
        "year": year,
        "doi": doi,
        "status": status,
        "category": category,
        "authors": authors,
        "rank": rank,
        "total": total,
        "truncated": truncated,
        "role": role_zh,
        "raw": body,
    }


def parse_cv() -> list[dict]:
    text = CV.read_text(encoding="utf-8")
    entries: list[dict] = []
    seen: set[tuple[str, ...]] = set()
    current = ""
    for line in text.splitlines():
        heading = re.match(r"^####\s+(.+)$", line)
        if heading:
            label = heading.group(1)
            current = next((cat for name, cat in SECTIONS.items() if label.startswith(name)), "")
            continue
        if re.match(r"^###", line):
            if "Publications" not in line:
                current = ""
            continue
        if not current:
            continue
        if not re.match(r"^\s*\d+\.\s+", line):
            continue
        entry = parse_entry(line, current)
        if not entry:
            continue
        # The CV repeats a few papers across sections; collapse on DOI first,
        # then on the title/venue/year triple when no DOI is given.
        key = (entry["doi"].lower() or f"{normalize_title(entry['title'])}|"
               f"{normalize_title(entry['venue'])}|{entry['year']}")
        if key in seen:
            continue
        seen.add(key)
        entries.append(entry)
    return entries


def existing_records() -> tuple[set[str], dict[str, str], list[dict]]:
    """Return DOI set, normalized-title map and a light index of mirror records.

    The mirror stores full titles while the CV abbreviates some of them, and
    older entries often carry no DOI, so a fuzzy first-author + year + venue
    index is kept as a third line of defence against duplicates.
    """
    dois: set[str] = set()
    titles: dict[str, str] = {}
    loose: list[dict] = []
    for folder in PAPERS.iterdir() if PAPERS.exists() else []:
        path = folder / "publication.yaml"
        if not path.is_dir() and not path.exists():
            continue
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        doi = str((doc.get("identifiers") or {}).get("doi") or "").strip().lower()
        if doi and doi != "None":
            dois.add(doi)
        key = normalize_title(str(doc.get("title") or ""))
        if key:
            titles[key] = folder.name
        authors = doc.get("authors") or []
        first = str(authors[0].get("name_en") or "") if authors and isinstance(authors[0], dict) else ""
        year = str((doc.get("lifecycle") or {}).get("pub_date") or "")[:4]
        loose.append(
            {
                "folder": folder.name,
                "first": family_of(first),
                "year": year,
                "venue": venue_tokens(str((doc.get("venue") or {}).get("name") or "")),
            }
        )
    return dois, titles, loose


def already_covered(entry: dict, dois: set[str], titles: dict[str, str], loose: list[dict]) -> str:
    """Return the mirror folder holding this CV entry, or "" when it is new."""
    if entry["doi"] and entry["doi"].lower() in dois:
        return "<doi>"
    if normalize_title(entry["title"]) in titles:
        return titles[normalize_title(entry["title"])]
    first = family_of(entry["authors"][0]["name_en"]) if entry["authors"] else ""
    venue = venue_tokens(entry["venue"])
    for rec in loose:
        if rec["first"] and rec["first"] == first and rec["year"] == entry["year"][:4]:
            if venue & rec["venue"]:
                return rec["folder"]
    return ""


def render(entry: dict) -> str:
    authors = []
    for author in entry["authors"]:
        item = {"name_en": author["name_en"], "role": author["role"]}
        authors.append(item)
    doc = {
        "synopsis": entry["slug"],
        "title": entry["title"],
        "venue": {"type": entry["venue_type"], "name": entry["venue"], "full_name": entry["venue"]},
        "lifecycle": {"status": entry["status"], "pub_date": entry["year"]},
        "identifiers": {"doi": entry["doi"] or None},
        "origin": {"source": "CV/LiXia.cv.en.md", "section": entry["category"]},
        "category": entry["category"],
        "role": entry["role"],
        "authorship": {"xia_rank": entry["rank"], "n_authors": entry["total"]},
        "authors": authors,
        "notes": "Backfilled from the CV (not in the Feishu mirror); verify before citing.",
    }
    header = (
        "# CV backfill - created by _generators/backfill_cv_papers.py.\n"
        "# Source: advisee/hc/0fund/00lcx-cv/LiXia.cv.en.md\n"
    )
    return header + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)


def render_record_md(entry: dict) -> str:
    names = ", ".join(
        a["name_en"] + ("*" if a["role"] == "corresponding_author" and a["name_en"] != SELF else "")
        for a in entry["authors"]
    )
    return (
        f"【类别】{'著作章节' if entry['category'] == 'book-chapter' else '论文成果'}\n"
        f"【时间】{entry['year']}\n"
        f"【标题】{entry['title']}\n"
        f"【本人角色】{entry['role'] or '合著'}（作者序 {entry['rank']}/{entry['total']}）\n\n"
        f"【结果】\n"
        f"状态={entry['status']};\n"
        f"期刊会议={entry['venue']};\n"
        f"DOI={entry['doi'] or '未知'};\n"
        f"作者序={names}（{entry['total']}）。\n\n"
        f"【证据】\n"
        f"CV（hc/0fund/00lcx-cv/LiXia.cv.en.md）回填，Feishu 镜像无此条。\n"
    )


def render_meta(entry: dict) -> str:
    import json

    meta = {
        "source": f"labxManage/Paper/{entry['slug']}",
        "record_id": "",
        "category": "Paper",
        "synopsis": entry["slug"],
        "status": entry["status"],
        "scope": "All",
        "post_date": entry["year"],
        "feishu_source": "CV-backfill",
        "mapping_kind": "cv_backfill",
    }
    return json.dumps(meta, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    entries = parse_cv()
    dois, titles, loose = existing_records()
    added: list[str] = []
    skipped: list[str] = []
    for entry in entries:
        hit = already_covered(entry, dois, titles, loose)
        if hit:
            skipped.append(f"{entry['slug']}  (mirror: {hit})")
            continue
        folder = PAPERS / entry["slug"]
        if folder.exists():
            continue
        added.append(entry["slug"])
        if dry:
            continue
        folder.mkdir(parents=True)
        (folder / "publication.yaml").write_text(render(entry), encoding="utf-8")
        (folder / "record.md").write_text(render_record_md(entry), encoding="utf-8")
        (folder / "meta.json").write_text(render_meta(entry), encoding="utf-8")

    print(f"CV entries parsed: {len(entries)}")
    print(f"Already covered by the mirror: {len(skipped)}")
    print(f"{'Would add' if dry else 'Added'}: {len(added)}")
    for slug in added:
        print(f"  + {slug}")
    if "--verbose" in argv:
        print("Covered:")
        for line in skipped:
            print(f"  = {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
