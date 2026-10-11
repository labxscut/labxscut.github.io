#!/usr/bin/env python3
"""Build _data/keywords.yml: a keyword cloud for the publications page.

Terms come from publication and abstract titles (venue names are excluded so
the cloud describes topics, not journals). Frequent generic scientific words
are dropped as stopwords. Each term records its count and the paper slugs it
appears in, so the cloud can size words by frequency and link each one to the
papers that carry it. Deterministic: same registry -> same output.

Usage (WSL):  python3 _generators/gen_keywords.py
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import yaml

from gen_publications import REPO

OUT = REPO / "_data" / "keywords.yml"

# Grammatical glue only. Topical words the lab actually works on (cancer,
# single cell, learning, network, genome, ...) are deliberately NOT here: the
# cloud should describe what the papers are about, so frequency alone decides.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "can",
    "do", "does", "for", "from", "had", "has", "have", "how", "its", "into",
    "in", "is", "it", "may", "no", "not", "of", "on", "or", "our", "than",
    "that", "the", "their", "them", "these", "this", "those", "to", "toward",
    "towards", "under", "up", "use", "used", "using", "via", "were", "what",
    "when", "where", "which", "who", "why", "will", "with", "without", "you",
    "also", "such", "each", "all", "any", "one", "two", "three", "new",
    "novel", "high", "low", "large", "small", "based", "between", "among",
    "during", "before", "after", "over", "about", "across", "within", "without",
}

# Generic academic glue that titles lean on regardless of subject: the
# artifact word ("abstract", "analysis"), the claim verbs ("accurate",
# "identifies"), and the umbrella nouns ("framework", "method"). Domain terms
# that name an actual method or object (association, prediction, integration,
# learning, sequencing) are kept, so the cloud reads as topics.
NOISE = {
    "abstract", "accurate", "accurately", "analysis", "analyses", "approach",
    "approaches", "associated", "characterization", "data", "dataset",
    "datasets", "discovery", "efficient", "effective", "feature", "features",
    "framework", "general", "generic", "high-throughput", "identification",
    "identify", "identifies", "identifying", "joint", "jointly", "large-scale",
    "method", "methods", "model", "models", "novel", "novelty", "profiling",
    "rare", "robust", "scale", "statistical", "statistically", "study",
    "studies", "tool", "tools", "unified",
    # fragments left when a hyphenated compound is not matched as a phrase
    "whole", "level", "relative", "throughput", "omics", "modal", "wide",
}

# Multi-word concepts worth keeping whole. Matched hyphen-tolerantly, so the
# phrase "single cell" also captures "single-cell"; the space form is emitted.
PHRASES = [
    "single cell", "whole genome", "deep learning", "network fusion",
    "similarity network", "structural variation", "copy number",
    "polygenic risk", "gene expression", "enzyme function", "liquid biopsy",
    "cancer subtype", "molecular subtype", "time series", "local similarity",
    "local association", "risk score", "multi omics", "multi modal",
    "high throughput", "genome wide", "cell free", "health seeking",
    "tumor microenvironment", "survival learning", "change point",
]

WORD = re.compile(r"[A-Za-z][A-Za-z]{3,}")


def phrase_pattern(phrase: str) -> re.Pattern[str]:
    # word boundaries with either a space or a hyphen between the words
    body = r"[\s\-]+".join(re.escape(part) for part in phrase.split())
    return re.compile(rf"(?<![a-z]){body}(?![a-z])")


def tokenize(title: str) -> list[str]:
    t = re.sub(r"[^a-z\s\-]", " ", title.lower())
    terms: list[str] = []
    # pull recognized phrases out first, emitting their canonical space form
    for phrase in PHRASES:
        pat = phrase_pattern(phrase)
        hits = pat.findall(t)
        if hits:
            terms.extend([phrase] * len(hits))
            t = pat.sub(" ", t)
    for w in WORD.findall(t):
        if w in STOPWORDS or w in NOISE:
            continue
        terms.append(w)
    return terms


def main() -> int:
    data = REPO / "_data"
    pubs = yaml.safe_load((data / "publications.yml").read_text(encoding="utf-8")) or []
    abstracts = yaml.safe_load((data / "abstracts.yml").read_text(encoding="utf-8")) or []
    records = [p for p in pubs if p.get("title")] + [a for a in abstracts if a.get("title")]

    counts: Counter[str] = Counter()
    slugs: dict[str, list[str]] = {}
    for rec in records:
        seen_in_title = set()
        for term in tokenize(rec["title"]):
            counts[term] += 1
            seen_in_title.add(term)
        for term in seen_in_title:
            slugs.setdefault(term, []).append(rec["slug"])

    # keep terms that appear at least twice, cap the cloud at 40
    terms = [t for t, c in counts.items() if c >= 2]
    terms.sort(key=lambda t: (-counts[t], t))
    terms = terms[:40]

    rows = [
        {
            "term": t,
            "count": counts[t],
            "slugs": sorted(slugs[t])[:12],
        }
        for t in terms
    ]
    header = (
        "# Generated by _generators/gen_keywords.py - do not hand-edit.\n"
        "# Keyword cloud for the publications page, from paper/abstract titles.\n"
        "# count drives font size; slugs are the matching publication anchors.\n"
    )
    OUT.write_text(
        header + yaml.safe_dump(rows, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    print(f"keywords: {len(rows)} terms from {len(records)} records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
