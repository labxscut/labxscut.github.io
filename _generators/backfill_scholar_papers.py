#!/usr/bin/env python3
"""Backfill labxManage paper records for the PI's public bibliography gaps.

``backfill_cv_papers.py`` covers everything the CV lists.  This script covers
the items that surface in Google Scholar / ORCID / Crossref but exist in
neither the Feishu mirror nor the CV: the 2005 SFI summer-school chapter, the
2008/2009 LSA conference abstracts, the 2013 PhD dissertation, a 2013
*Genetics and Molecular Research* article, five AACR meeting abstracts and five
openRxiv preprints (including the sxLaep preprint, the only publication behind
the sxLaep tool).

Records are written under ``~/work/advisee/hc/labxManage/Paper/<slug>/`` with
the same schema as the Feishu mirror plus three explicit gate fields:

``visibility``          ``registry`` for archival items, ``scholar-only`` for
                        abstracts / preprints / the thesis.
``published_on_site``   whether the item may ever reach ``_data/publications.yml``.
``lifecycle.status``    still non-public (``Preprint`` / ``Meeting`` / ``Thesis``)
                        so ``gen_publications.py`` excludes it until a human
                        promotes the record.

``origin`` records where the item came from and ``related.twin`` names the
published registry record an abstract or preprint became, so the duplication is
visible instead of silent.

Usage (Git Bash / WSL / Windows Python):
    python _generators/backfill_scholar_papers.py --dry-run
    python _generators/backfill_scholar_papers.py
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

import yaml

WORK = Path(os.environ.get("LABX_WORK", "/mnt/d/work"))
PAPERS = WORK / "advisee" / "hc" / "labxManage" / "Paper"

FIRST = "first_author"
CORRESPONDING = "corresponding_author"
CO = "co_author"
SOLE = "sole_author"

# One entry per gap item, transcribed from tmp/scholar_pubs.yaml (ORCID works +
# Crossref).  ``authors`` is the full public author list; the PI's rank/role is
# derived from it so the record stays self-consistent.
ITEMS: list[dict] = [
    {
        "slug": "FamilyCSSS2005CorrelatingCategories",
        "title": "Correlating Extracted Categories from Two Separate Databases",
        "year": "2005",
        "venue": {
            "type": "book",
            "name": "SFI Complex Systems Summer School",
            "full_name": "SFI Complex Systems Summer School Proceedings, Beijing, China",
        },
        "status": "Published",
        "category": "book-chapter",
        "authors": ["Neiloufar Family", "Eric Miller", "Li Xia", "Miao-Hsuen Yen"],
        "xia_rank": 3,
        "role": CO,
        "visibility": "registry",
        "published_on_site": False,
        "origin": {
            "source": "Google Scholar / ORCID survey",
            "section": "Book Chapters",
            "detail": "BibTeX @incollection in the SFI summer-school volume; ORCID mislabels it journal-article.",
        },
        "notes": "Pre-SCappointment student work, no DOI. The ORCID PDF link is an expired signed CloudFront URL - re-fetch the citation before citing.",
    },
    {
        "slug": "XiaISMB2008LSAWebService",
        "title": "LSA: A web service for local similarity analysis of time sequence data",
        "year": "2008",
        "venue": {
            "type": "conference",
            "name": "ISMB 2008",
            "full_name": "16th Annual International Conference on Intelligent Systems for Molecular Biology (ISMB), poster",
        },
        "status": "Meeting",
        "category": "research",
        "authors": ["Li Xia", "Jed A Fuhrman", "Fengzhu Sun"],
        "xia_rank": 1,
        "role": FIRST,
        "tool": {"name": "LSA (web service)", "url": "https://github.com/labxscut/elsa", "key": "sxELA"},
        "visibility": "scholar-only",
        "published_on_site": False,
        "twin": "XiaBioinf2013EfficientStatisticalSignifi",
        "origin": {
            "source": "Google Scholar / ORCID survey",
            "section": "Conference Talks / Posters",
            "detail": "Conference poster / abstract, not an archival full-text publication; no DOI.",
            "see_also": "CV lists the LSA web service under Conference Talks/Posters for ISMB 2010; Scholar/ORCID date it 2008.",
        },
        "notes": "Poster abstract only. Resolve the ISMB 2008 vs 2010 year conflict before publishing.",
    },
    {
        "slug": "XiaRECOMB2009PairTriplet",
        "title": "Inferring Pair and Triplet Interactions from Time Series Ecological Data",
        "year": "2009",
        "venue": {
            "type": "conference",
            "name": "RECOMB 2009",
            "full_name": "13th Annual International Conference on Research in Computational Molecular Biology (RECOMB), poster",
        },
        "status": "Meeting",
        "category": "research",
        "authors": ["Li Xia", "Joshua A Steele", "Jed A Fuhrman", "Fengzhu Sun"],
        "xia_rank": 1,
        "role": FIRST,
        "tool": {"name": "LSA", "url": "https://github.com/labxscut/elsa", "key": "sxELA"},
        "visibility": "scholar-only",
        "published_on_site": False,
        "twin": "XiaBSB2011ExtendedLocalSimilarity",
        "origin": {
            "source": "Google Scholar / ORCID survey",
            "section": "Conference Talks / Posters",
            "detail": "Conference poster / abstract, not an archival full-text publication; no DOI.",
        },
        "notes": "Poster abstract; the method became eLSA (BSB 2011 / Bioinformatics 2013).",
    },
    {
        "slug": "XiaUSC2013PhDThesis",
        "title": "Developing statistical and algorithmic methods for shotgun metagenomics and time series analysis",
        "year": "2013",
        "venue": {
            "type": "other",
            "name": "USC dissertation",
            "full_name": "PhD dissertation, University of Southern California",
        },
        "status": "Thesis",
        "category": "research",
        "authors": ["Li Charlie Xia"],
        "xia_rank": 1,
        "role": SOLE,
        "visibility": "registry",
        "published_on_site": False,
        "origin": {
            "source": "Google Scholar / ORCID survey",
            "section": "Dissertations and Thesis",
            "detail": "Doctoral dissertation, University of Southern California - not a journal article.",
        },
        "notes": "Advisor: Jed A. Fuhrman. Add the ProQuest / USC library handle when known.",
    },
    {
        "slug": "WangGMR2013ThelperDifferentiation",
        "title": "Genetic analysis of differentiation of T-helper lymphocytes",
        "year": "2013",
        "venue": {
            "type": "journal",
            "name": "Genetics and Molecular Research",
            "full_name": "Genetics and Molecular Research",
        },
        "doi": "10.4238/2013.APRIL.2.13",
        "status": "Published",
        "category": "collaborative",
        "authors": ["Q. Wang", "M. Li", "L.C. Xia", "G. Wen", "H. Zu", "M. Gao"],
        "xia_rank": 3,
        "role": CO,
        "visibility": "registry",
        "published_on_site": True,
        "origin": {
            "source": "Google Scholar / ORCID survey",
            "section": "Collaborative Articles",
            "detail": "Peer-reviewed article with DOI; absent from both the CV and the Feishu mirror.",
        },
        "notes": "Collaborative (non-LSA) clinical paper. PI role unknown from Scholar - verify against the PDF before promoting.",
    },
]

# AACR meeting abstracts published as Cancer Research supplements.
AACR = [
    (
        "XiaCR2015Abstract4871",
        "Abstract 4871: A new multiple feature approach for rapid and highly accurate somatic structural variation discovery from whole cancer genome sequencing",
        "2015",
        "10.1158/1538-7445.AM2015-4871",
        ["Li C. Xia", "John Bell", "Jiamin Chen", "Nancy R. Zhang", "Hanlee P. Ji"],
        1,
        FIRST,
        None,
    ),
    (
        "AndorCR2016Abstract2387",
        "Abstract 2387: Pan-cancer analysis of clonal evolution reveals the costs and adaptive benefits of genomic instability",
        "2016",
        "10.1158/1538-7445.AM2016-2387",
        ["Noemi Andor", "Trevor A. Graham", "Marnix Jansen", "Li C. Xia", "Athena Aktipis", "Claudia Petritsch", "Hanlee P. Ji", "Carlo C. Maley"],
        4,
        CO,
        None,
    ),
    (
        "XiaCR2018Abstract4334",
        "Abstract 4334: Linked read whole genome sequencing reveals pervasive chromosomal level instability and novel rearrangements in brain metastases from colorectal cancer",
        "2018",
        "10.1158/1538-7445.AM2018-4334",
        ["Li C. Xia", "John M. Bell", "Christina Wood-Bouwens", "Daniel A. King", "GiWon Shin", "Stephanie Greer", "Ian D. Connolly", "Melanie H. Gephart", "Hanlee P. Ji"],
        1,
        FIRST,
        None,
    ),
    (
        "LeeCR2018Abstract438",
        "Abstract 438: High-quality CNV segments from low-coverage whole genome sequencing from FFPE cancer biopsies based on an evaluation of multiple CNV tools",
        "2018",
        "10.1158/1538-7445.AM2018-438",
        ["HoJoon Lee", "Li Charlie Xia", "Stephanie Greer", "John Bell", "Sue M. Grimes", "Christina Wood Bouwens", "Giwon Shin", "Billy TC Lau", "Lucas Johnson", "Noemi Andor", "Kenneth Day", "Mickey Miller", "Helaman Escobar", "Lincoln Nadauld", "Hanlee P. Ji", "Paul Van Hummelen"],
        2,
        CO,
        None,
    ),
    (
        "XiaCR2019Abstract5022",
        "Abstract 5022: iGRAMMy: Cloud-based characterization of microbial landscape in colorectal cancers",
        "2019",
        "10.1158/1538-7445.AM2019-5022",
        ["Li C. Xia", "Dongmei Ai", "Man Guo", "Hanlee Ji"],
        1,
        FIRST,
        {"name": "iGRAMMy", "url": "https://github.com/labxscut/grammy"},
    ),
]
for slug, title, year, doi, authors, rank, role, tool in AACR:
    item = {
        "slug": slug,
        "title": title,
        "year": year,
        "venue": {
            "type": "conference",
            "name": "AACR Annual Meeting",
            "full_name": f"AACR Annual Meeting {year} Abstracts (Cancer Research)",
        },
        "doi": doi,
        "status": "Meeting",
        "category": "research" if role == FIRST else "collaborative",
        "authors": authors,
        "xia_rank": rank,
        "role": role,
        "visibility": "scholar-only",
        "published_on_site": False,
        "origin": {
            "source": "Google Scholar / ORCID survey",
            "section": "Posters",
            "detail": "Peer-reviewed meeting abstract with DOI; not a full research article.",
            "see_also": "CV '#### Posters' covers the AACR abstracts (iGRAMMy = AACR 2019).",
        },
        "notes": "Meeting abstract; do not count it as a research article.",
    }
    if tool:
        item["tool"] = tool
    ITEMS.append(item)

# Preprints (openRxiv / the lab preprint server).
PREPRINTS = [
    (
        "LiuopenRxiv2021SeqDistK",
        "SeqDistK: a Novel Tool for Alignment-free Phylogenetic Analysis",
        "2021",
        "10.1101/2021.08.16.456500",
        ["Xuemei Liu", "Wen Li", "Guanda Huang", "Tianlai Huang", "Qingang Xiong", "Wen Chen", "Li C. Xia"],
        7,
        {"name": "SeqDistK (released as KSaK)", "url": "https://github.com/labxscut/ksak"},
        "Alignment-free phylogeny preprint; the software later shipped as KSaK.",
    ),
    (
        "XieopenRxiv2023BreastCancerModel",
        "Building a genetic and epigenetic predictive model of breast cancer intrinsic subtypes using large-scale data and hierarchical structure learning",
        "2023",
        "10.1101/2023.06.12.544702",
        ["Jiemin Xie", "Binyu Yang", "Keyi Li", "Lixin Gao", "Xuemei Liu", "Yunhui Xiong", "Wen Chen", "Li C. Xia"],
        8,
        {"name": "DeepLB", "url": "https://github.com/labxscut/DeepLB", "key": "deeplb"},
        "Preprint of the DeepLB modelling line; the journal version (LiangGB2025DeepLB) is under review.",
    ),
    (
        "YuopenRxiv2024MultiTraitHF",
        "Multi-trait genome-wide analysis identified novel risk loci and candidate drugs for heart failure",
        "2024",
        "10.1101/2024.03.24.24304812",
        ["Zhengyang Yu", "Maohuan Lin", "Zhanyu Liang", "Bozhen Ren", "Ying Yang", "Wen Chen", "Yonghua Wang", "Xiaoling Lin", "Yangxin Chen", "Kaida Ning", "Li C. Xia"],
        11,
        None,
        "Preprint of the published Human Genetics and Genomics Advances article (YuHGGadv2025MtagHF).",
    ),
    (
        "DuanopenRxiv2024EnzHier",
        "Predicting Enzyme Functions Using Contrastive Learning with Hierarchical Enzyme Structure Information",
        "2024",
        "10.1101/2024.07.07.602424",
        ["Hongyu Duan", "Ziyan Li", "Yixuan Wu", "Wen Chen", "Li C Xia"],
        5,
        {"name": "EnzHier", "url": "https://github.com/labxscut/EnzHier", "key": "sxEnzHier"},
        "Preprint of the ISBRA 2025 / JCB EnzHier papers.",
    ),
    (
        "DuanPreprint2026SxLaep",
        "sxLaep: a Lightweight and Accurate Enzyme Predictor",
        "2026",
        "10.64898/2026.05.06.723393",
        ["Hongyu Duan", "Xinyu Han", "Yijun Mo", "Bozhen Ren", "Li C. Xia"],
        5,
        {"name": "sxLaep", "url": "https://github.com/labxscut/sxLaep", "key": "sxLaep"},
        "Only publication to date for the sxLaep tool.",
    ),
]
for slug, title, year, doi, authors, rank, tool, note in PREPRINTS:
    ITEMS.append(
        {
            "slug": slug,
            "title": title,
            "year": year,
            "venue": {
                "type": "preprint",
                "name": "openRxiv" if doi.startswith("10.1101/") else "Preprint",
                "full_name": (
                    "openRxiv preprint"
                    if doi.startswith("10.1101/")
                    else "Lab preprint (10.64898)"
                ),
            },
            "doi": doi,
            "status": "Preprint",
            "category": "collaborative",
            "authors": authors,
            "xia_rank": rank,
            "role": CORRESPONDING,
            "tool": tool,
            "visibility": "scholar-only",
            "published_on_site": False,
            "origin": {
                "source": "Google Scholar / ORCID survey",
                "section": "In-Progress Articles",
                "detail": "Preprint server record; not peer reviewed.",
            },
            "notes": note,
        }
    )


def normalize_title(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", text.lower())
    return re.sub(r"[^a-z0-9]+", "", text)


def is_self(name: str) -> bool:
    parts = re.sub(r"[^A-Za-z. ]", " ", str(name)).lower().split()
    return "xia" in parts or "xia," in parts or any(p.startswith("xia") for p in parts)


def author_role(name: str, index: int, total: int, pi_role: str) -> str:
    if is_self(name):
        if pi_role == SOLE:
            return SOLE
        if index == 0 and pi_role == FIRST:
            return FIRST
        if index == total - 1 and pi_role in {CORRESPONDING, FIRST}:
            return CORRESPONDING
        return CO
    return "first_author" if index == 0 else "co_author"


def load(path: Path) -> dict | None:
    try:
        return yaml.safe_load(io.open(path, encoding="utf-8", errors="replace").read())
    except Exception:
        return None


def registry() -> tuple[set[str], set[str], set[str]]:
    """Existing folders, DOIs and normalized titles already covered."""
    folders, dois, titles = set(), set(), set()
    if not PAPERS.is_dir():
        return folders, dois, titles
    for folder in sorted(PAPERS.iterdir()):
        record = folder / "publication.yaml"
        if not folder.is_dir() or not record.is_file():
            continue
        folders.add(folder.name)
        doc = load(record)
        if not isinstance(doc, dict):
            continue
        doi = str((doc.get("identifiers") or {}).get("doi") or "").strip().lower()
        if doi and doi != "null":
            dois.add(doi)
        title = str(doc.get("title") or "").strip()
        if title:
            titles.add(normalize_title(title))
    return folders, dois, titles


def render(item: dict) -> str:
    total = len(item["authors"])
    authors = [
        {"name_en": name, "role": author_role(name, i, total, item["role"])}
        for i, name in enumerate(item["authors"])
    ]
    doc = {
        "synopsis": item["slug"],
        "title": item["title"],
        "venue": item["venue"],
        "lifecycle": {"status": item["status"], "pub_date": item["year"]},
        "identifiers": {"doi": item.get("doi") or None},
        "origin": item["origin"],
        "visibility": item["visibility"],
        "published_on_site": item["published_on_site"],
        "category": item["category"],
        "role": item["role"],
        "authorship": {"xia_rank": item["xia_rank"], "n_authors": total},
        "authors": authors,
        "notes": item["notes"],
    }
    tool = item.get("tool") or {}
    if tool.get("name"):
        doc["software"] = {
            "name": tool.get("name"),
            "url": tool.get("url"),
            "tool_key": tool.get("key"),
        }
    if item.get("twin"):
        doc["related"] = {"twin": item["twin"]}
    header = (
        "# Scholar backfill - created by _generators/backfill_scholar_papers.py.\n"
        "# Source: Google Scholar / ORCID / Crossref survey of the PI bibliography;\n"
        "# not present in the Feishu mirror (hc/labxManage) or in the CV.\n"
    )
    return header + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)


def render_md(item: dict) -> str:
    total = len(item["authors"])
    names = ", ".join((n + "*" if is_self(n) else n) for n in item["authors"])
    tool = item.get("tool") or {}
    lines = [
        "【类别】" + ("著作章节" if item["category"] == "book-chapter" else "论文成果"),
        f"【时间】{item['year']}",
        f"【标题】{item['title']}",
        f"【本人角色】{item['role']}（作者序 {item['xia_rank']}/{total}）",
        "",
        "【结果】",
        f"状态={item['status']};",
        f"期刊会议={item['venue']['full_name']};",
        f"DOI={item.get('doi') or '未知'};",
        f"作者={names}（{total}）。",
    ]
    if tool.get("name"):
        lines.append(f"软件={tool['name']} ({tool.get('url', '')});")
    lines += [
        "",
        "【证据】",
        item["origin"].get("detail", ""),
        item["origin"].get("see_also", ""),
        "来源：Google Scholar / ORCID / Crossref 公共文献库调查；Feishu 镜像与 CV 均无此条。",
    ]
    if item.get("twin"):
        lines.append(f"已发表版本：labxManage/Paper/{item['twin']}")
    return "\n".join(line for line in lines if line) + "\n"


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    folders, dois, titles = registry()
    created = skipped = 0
    for item in ITEMS:
        doi = (item.get("doi") or "").lower()
        if (doi and doi in dois) or normalize_title(item["title"]) in titles:
            skipped += 1
            print(f"[skip] {item['slug']}  (already in registry)")
            continue
        if item["slug"] in folders:
            skipped += 1
            print(f"[skip] {item['slug']}  (folder exists)")
            continue
        print(
            f"{'[dry] ' if dry else ''}{item['slug']}  {item['year']}  {item['status']:<9} "
            f"{item['visibility']:<12} site={item['published_on_site']}  {item['title'][:44]}"
        )
        if not dry:
            folder = PAPERS / item["slug"]
            folder.mkdir(parents=True, exist_ok=True)
            io.open(folder / "publication.yaml", "w", encoding="utf-8", newline="\n").write(render(item))
            io.open(folder / "record.md", "w", encoding="utf-8", newline="\n").write(render_md(item))
            io.open(folder / "meta.json", "w", encoding="utf-8", newline="\n").write(
                json.dumps(
                    {
                        "source": f"labxManage/Paper/{item['slug']}",
                        "origin": "scholar-survey",
                        "visibility": item["visibility"],
                        "status": item["status"],
                        "post_date": item["year"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n"
            )
            folders.add(item["slug"])
        created += 1
    print(f"scholar records: {created} created, {skipped} already covered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
