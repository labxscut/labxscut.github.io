#!/usr/bin/env python3
"""Harvest publisher-authoritative author names into the labxManage registry.

Backlog 3.20 wants every publication author rendered as "First M. Last",
retrieved online when the local record does not carry it, falling back to the
"LM Last" initials form only when retrieval fails.

The registry's own ``authors[].name_en`` comes from the CV or the Feishu mirror
and often uses the CV-era concatenated-initials form ("LC Xia", "DM Ai"). It
holds no ORCIDs and its harvested ``citation:`` block stores only
volume/issue/pages/dates -- never an author list. Crossref does return the
publisher's given/family split, so that is real evidence rather than invention.

SAFETY GATE (this is what makes it evidence, not a guess)
    A record is harvested only when the publisher list aligns POSITIONALLY with
    the registry list: same length, and at every index the registry name and the
    publisher name agree on surname AND on given-name initials. Surname matching
    is order-agnostic and particle-tolerant because the registry stores both
    Western ("Hongyu Duan") and Chinese ("Ai Dongmei") order and the CV drops
    particles ("PV Hummelen" for "Paul Van Hummelen"). Anything that does not
    pass is reported with a reason and NEVER written.

Writes ``citation.authors`` (plus ``authors_source``/``authors_fetched``) into
``publication.yaml``, mirroring how the existing ``citation:`` block already
records Crossref harvests. Idempotent: re-running with unchanged upstream data
produces no diff.

Usage:
    python _generators/harvest_author_names.py --dry-run
    python _generators/harvest_author_names.py --write
    python _generators/harvest_author_names.py --dry-run --slug AiBG2019ExploreMediatedCo
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

import yaml

WORK = Path(os.environ.get("LABX_WORK", "/mnt/d/work"))
PAPERS = WORK / "advisee" / "hc" / "labxManage" / "Paper"
UA = "LabX-registry-harvest/1.0 (mailto:lcxia@scut.edu.cn)"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)


# --------------------------------------------------------------------- matching
def letters_only(s: str) -> str:
    return re.sub(r"[^a-z]", "", (s or "").lower())


# Surname particles that Crossref/DataCite often leave in the GIVEN field
# ("Paul Van" + family "Hummelen"). They belong to the surname, so they must be
# spelled out rather than abbreviated to an initial -- "Paul V. Hummelen" would
# be a different, wrong name.
PARTICLES = {
    "van", "von", "der", "den", "de", "del", "della", "di", "da", "dos", "du",
    "la", "le", "ten", "ter", "het", "bin", "binti", "al", "el", "st", "mc",
    "mac", "af", "av", "dos", "e", "y",
}


def display_name(given: str, family: str) -> str:
    """Render a publisher given/family pair as the site's "First M. Last" form.

    Backlog 3.20 sets this target: the first given name is spelled out, later
    ones are reduced to initials, and the surname follows. A single-letter token
    keeps its dot ("J Michael" -> "J. M."). Surname particles are never
    abbreviated, because "Van" is part of the surname, not a middle name.

    Falls back gracefully: no given name yields the bare surname, which is the
    most the evidence supports.
    """
    fam = (family or "").strip()
    parts = [p for p in re.split(r"\s+", (given or "").strip()) if p]
    if not parts:
        return fam
    out = []
    for i, tok in enumerate(parts):
        core = tok.strip(".").strip()
        if not core:
            continue
        if i > 0 and core.lower().rstrip(".") in PARTICLES:
            out.append(core)                      # keep "Van" spelled out
        elif len(core) == 1:
            out.append(core.upper() + ".")        # already an initial
        elif i == 0:
            out.append(core)                      # first given name in full
        else:
            out.append(core[0].upper() + ".")     # later given names -> initial
    rendered = " ".join(out)
    return f"{rendered} {fam}".strip() if fam else rendered


def name_tokens(name: str) -> list[tuple[str, str]]:
    """Ordered tokens of a name, each tagged as an abbreviation or a full word.

    ("initial", letter) for an abbreviated token, ("word", letters) for a
    spelled-out one. The distinction is the whole basis of the matching rule: a
    registry *word* is an assertion about the actual given name and must match
    exactly, while a registry *initial* is an abbreviation that the publisher's
    fuller form is allowed to expand.

    An all-caps letter run is an abbreviation whether or not it was dotted, so
    "LC", "L.C." and "L. C." all yield the initials l, c. Treating "L.C." as a
    single word "lc" instead would make it unmatchable against the publisher's
    "Li C." and would fail the roster guard on the PI's own name.

    "PV Hummelen"  -> [("initial","p"), ("initial","v"), ("word","hummelen")]
    "L.C. Xia"     -> [("initial","l"), ("initial","c"), ("word","xia")]
    "Ai Dongmei"   -> [("word","ai"), ("word","dongmei")]
    "Xia Li C."    -> [("word","xia"), ("word","li"), ("initial","c")]
    """
    out: list[tuple[str, str]] = []
    for tok in re.split(r"\s+", (name or "").strip()):
        tok = tok.strip(".").strip()
        if not tok:
            continue
        bare = tok.replace(".", "")
        if re.fullmatch(r"[A-Za-z]{2,}", bare) and bare.isupper():
            out.extend(("initial", c.lower()) for c in bare)  # "PV"|"P.V." -> p, v
        elif re.fullmatch(r"[A-Za-z]", bare):
            out.append(("initial", bare.lower()))             # "C." -> c
        else:
            out.append(("word", letters_only(tok)))           # "Dongmei"
    return out


def hyphen_tokens(name: str) -> list[tuple[str, str]]:
    """Tokens of a name, splitting on whitespace AND hyphens.

    A hyphen joins two given names ("Cheryl-Emiliane", "Li-San", "Jean-Pierre"),
    each of which answers to one registry initial or one publisher word, so they
    must pair separately. Without this, registry "CET Chow" cannot match the
    publisher's "Cheryl-Emiliane T Chow" (the single token "cherylemiliane" would
    have to absorb both C and E), and registry "Wang Li-San" cannot match the
    publisher's given "Li-San" ("lisan" vs "li").

    Hyphenated SURNAMES still work because split_surname rejoins a contiguous run
    of words and surname_candidates includes the de-hyphenated form, so
    "C Wood-Bouwens" against family "Wood-Bouwens" still matches.
    """
    out: list[tuple[str, str]] = []
    for part in re.split(r"[\s\-]+", (name or "").strip()):
        out.extend(name_tokens(part))
    return out


# Kept as an alias: the publisher given field is the most common caller.
given_name_tokens = hyphen_tokens


def surname_candidates(publisher_family: str) -> set[str]:
    """Accept the full family string, its last token, and its hyphen-joined form.

    Covers CV-dropped particles: registry "PV Hummelen" has surname token
    "hummelen", publisher family is "Van Hummelen" -> {"vanhummelen", "hummelen"}.
    """
    fam = (publisher_family or "").strip()
    out = {letters_only(fam)}
    toks = [letters_only(t) for t in re.split(r"[\s\-]+", fam) if t]
    if toks:
        out.add(toks[-1])
        out.add("".join(toks))
    return {o for o in out if o}


def split_surname(reg_name: str, surs: set[str]) -> tuple[list[str], list[tuple[str, str]]] | None:
    """Split a registry name into (surname words, given tokens).

    The surname may be several words ("Van Hummelen") and may sit at either end
    ("Sun Thomas Yang" is surname-first), so try every contiguous run of the
    registry's full words and keep the LONGEST one that equals a publisher
    surname candidate. Longest-first is what stops "Van Hummelen Paul" from
    being read as surname "Hummelen" with a stray given word "Van", and what
    keeps a hyphenated surname ("C Wood-Bouwens") attached as one surname rather
    than reading "Bouwens" alone and leaving "Wood" behind as a given name.
    """
    toks = hyphen_tokens(reg_name)
    words = [(i, v) for i, (k, v) in enumerate(toks) if k == "word"]
    best = None
    for a in range(len(words)):
        for b in range(a + 1, len(words) + 1):
            span = words[a:b]
            # Contiguous in the original token order, so a particle stays attached.
            if span[-1][0] - span[0][0] != len(span) - 1:
                continue
            joined = "".join(v for _, v in span)
            if joined in surs and (best is None or len(span) > len(best)):
                best = span
    if best is None:
        return None
    used = {i for i, _ in best}
    surname = [v for _, v in best]
    given = [(k, v) for i, (k, v) in enumerate(toks) if i not in used]
    return surname, given


def token_compatible(reg: tuple[str, str], pub: tuple[str, str]) -> bool:
    """Compare one registry given token with one publisher given token.

    This asymmetry is the whole safety argument:
      * a registry WORD is an assertion about the real given name, so the
        publisher must spell it identically (or abbreviate it to its initial).
        This is what rejects "Yang Wang" against the publisher's "Yonghua Wang"
        -- two different people who share a surname and a first letter.
      * a registry INITIAL is an abbreviation, so the publisher is allowed to
        expand it. This is what accepts "LC Xia" against "Li Charlie Xia" and
        "DM Ai" against "Dongmei Ai", which is exactly the normalization wanted.
    """
    rk, rv = reg
    pk, pv = pub
    if rk == "word":
        return rv == pv if pk == "word" else pv == rv[:1]
    return pv.startswith(rv) if pk == "word" else pv == rv


def position_matches(reg_name: str, pub: dict) -> tuple[bool, str]:
    """True when one registry name and one publisher author are the same person."""
    family = (pub.get("family") or "").strip()
    given = (pub.get("given") or "").strip()
    if not family:
        return False, "publisher record has no family name"
    surs = surname_candidates(family)
    split = split_surname(reg_name, surs)
    if split is None:
        reg_words = [v for k, v in name_tokens(reg_name) if k == "word"]
        return False, f"surname '{reg_words}' not in publisher '{sorted(surs)}'"

    _surname, reg_given = split
    pub_given = given_name_tokens(given)
    if not reg_given:
        return True, "surname-only registry name"
    if not pub_given:
        return False, "publisher record has no given name"

    # Pair by position. The publisher may carry MORE given tokens than the
    # registry (it spells out what the CV abbreviated) -- that extra detail is
    # the point of the harvest, so it is allowed. The registry carrying more
    # than the publisher is also allowed (the publisher abbreviated).
    for i, rt in enumerate(reg_given):
        if i < len(pub_given) and not token_compatible(rt, pub_given[i]):
            return False, (f"given token {i}: registry {rt} vs publisher {pub_given[i]}")
    return True, "given name compatible"


def strip_honorific(name: str) -> str:
    """Drop a leading title so roster "Dr. Li C. Xia" compares as "Li C. Xia".

    The roster stores an honorific for faculty rows; the publisher never does.
    Without this the guard would reject the PI's own name.
    """
    return re.sub(r"^(Dr\.?|Prof\.?|Professor|Mr\.?|Ms\.?|Mrs\.?)\s+", "",
                  (name or "").strip(), flags=re.IGNORECASE).strip()


def align(reg_names: list[str], pub_authors: list[dict],
          roster_of: dict[str, str] | None = None) -> tuple[list[dict] | None, str]:
    """Match each registry author to a publisher author, or return None.

    On success returns a list PARALLEL to ``reg_names`` holding the publisher
    record for that same person. Returning the pairing (not just a verdict) is
    what lets the caller normalize the registry's own list in place, which is
    the only safe thing to do when the registry keeps fewer authors than the
    publisher lists.

    ``roster_of`` maps a registry author name to the lab roster's authoritative
    ``name_en`` for that person, when the site's own guarded lookup resolves it.
    When present it adds a second, stricter test: the publisher name must agree
    with the ROSTER too, not merely with the registry's abbreviated form.

    That matters because initials alone cannot distinguish people. "LC Xia"
    matches both "Li C. Xia" and "Lu C. Xia", and the first is the PI. The
    registry string is evidence of position; the roster is evidence of identity.

    Two modes, tried in order:
      1. POSITIONAL -- same length and every index agrees. This is the strong
         guarantee and covers records whose registry list is complete.
      2. SUBSET -- the registry list is shorter (CV-era records often keep only
         the lab-relevant authors, e.g. 3 of 15). Then every registry author must
         match exactly ONE publisher author and no publisher author may be
         claimed twice. Injectivity is what keeps this from being a guess: an
         ambiguous surname ("two Wangs") fails the record instead of picking one.
    """
    if not reg_names:
        return None, "registry record has no author list"
    if not pub_authors:
        return None, "publisher returned no author list"

    if len(reg_names) == len(pub_authors):
        for i, (rn, pa) in enumerate(zip(reg_names, pub_authors)):
            ok, why = _check_pair(rn, pa, roster_of, i)
            if not ok:
                return None, why
        return list(pub_authors), f"all {len(reg_names)} positions match"

    if len(reg_names) > len(pub_authors):
        return None, (f"count mismatch: registry {len(reg_names)} vs "
                      f"publisher {len(pub_authors)}")
    return _align_subset(reg_names, pub_authors, roster_of)


def _check_pair(rn: str, pa: dict, roster_of: dict[str, str] | None,
                i: int) -> tuple[bool, str]:
    """One registry name against one publisher author, plus the roster guard."""
    ok, why = position_matches(rn, pa)
    if not ok:
        return False, f"position {i} ('{rn}'): {why}"
    roster_name = (roster_of or {}).get(rn)
    if roster_name:
        ok_r, why_r = position_matches(roster_name, pa)
        if not ok_r:
            return False, (f"position {i}: publisher '{pa.get('given')} "
                           f"{pa.get('family')}' contradicts the lab roster's "
                           f"'{roster_name}' ({why_r})")
    return True, "ok"


def initials_set(name: str) -> tuple[frozenset[str], frozenset[str]]:
    """(surname words, given initials) of a name, both as unordered sets."""
    toks = hyphen_tokens(name)
    words = frozenset(v for k, v in toks if k == "word")
    inits = frozenset(v for k, v in toks if k == "initial")
    return words, inits


def _relaxed_match(rn: str, pa: dict, roster_of: dict[str, str] | None) -> bool:
    """Order-insensitive fallback for a name the strict test rejected.

    Deliberately narrow. It fires only when ALL of these hold:
      * the registry name is initials-only for its given part ("CT Boles");
      * the publisher surname equals a registry surname word;
      * the two given-initial SETS are identical, so no letter is invented;
      * the publisher's own given words are consistent with those initials.

    That covers a real pattern in this corpus: the CV wrote "CT Boles" while the
    publisher records "T Christian Boles" -- one person, initials listed in the
    other order. It still rejects a differing initial set, and the caller
    additionally requires the match to be unique across the whole author list, so
    a paper containing two authors who share a surname cannot be resolved this
    way.
    """
    reg_words, reg_inits = initials_set(rn)
    if not reg_inits:
        return False                      # a spelled-out given name must match exactly
    surs = surname_candidates(pa.get("family") or "")
    if not (reg_words & surs):
        return False
    pub_given = hyphen_tokens(pa.get("given") or "")
    # Every registry initial must be accounted for by a publisher given word's
    # first letter or by a publisher given initial.
    accounted = {v[0] for k, v in pub_given if k == "word"}
    accounted |= {v for k, v in pub_given if k == "initial"}
    if not reg_inits <= accounted:
        return False
    roster_name = (roster_of or {}).get(rn)
    if roster_name:
        rw, ri = initials_set(roster_name)
        if not (rw & surs):
            return False
        # The roster spells the member's name out, so its WORDS stay strict:
        # "Li C. Xia" must not be relaxed into accepting the publisher's "Lu".
        # Only the registry's own initials were allowed to be reordered.
        pub_words = {v for k, v in pub_given if k == "word"}
        for w in rw:
            if w in surs:
                continue
            if w not in pub_words:
                return False
        if ri and not ri <= accounted:
            return False
    return True


def _align_subset(reg_names: list[str], pub_authors: list[dict],
                  roster_of: dict[str, str] | None) -> tuple[list[dict] | None, str]:
    """Match a shorter registry list injectively into the publisher list."""
    claimed: set[int] = set()
    matched: list[dict] = []
    for rn in reg_names:
        hits = []
        for j, pa in enumerate(pub_authors):
            if j in claimed:
                continue
            ok, _ = position_matches(rn, pa)
            if not ok:
                continue
            roster_name = (roster_of or {}).get(rn)
            if roster_name:
                ok_r, _ = position_matches(roster_name, pa)
                if not ok_r:
                    continue
            hits.append(j)
        if not hits:
            # Nothing matched strictly. Try the order-insensitive fallback, but
            # only where the surname is unique in the author list so the match
            # cannot silently pick between two different people.
            for j, pa in enumerate(pub_authors):
                if j in claimed:
                    continue
                if _relaxed_match(rn, pa, roster_of):
                    hits.append(j)
            if len(hits) == 1:
                sur = surname_candidates(pub_authors[hits[0]].get("family") or "")
                same_surname = [j for j, p in enumerate(pub_authors)
                                if surname_candidates(p.get("family") or "") & sur]
                if len(same_surname) != 1:
                    hits = []   # ambiguous surname: refuse rather than guess
        if len(hits) != 1:
            return None, (f"'{rn}' matched {len(hits)} publisher author(s); "
                          f"a subset match must be unique")
        claimed.add(hits[0])
        matched.append(pub_authors[hits[0]])
    return matched, f"all {len(reg_names)} registry authors matched uniquely (subset)"


# ----------------------------------------------------------------------- fetch
def crossref_authors(doi: str) -> tuple[list[dict] | None, str]:
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    p = subprocess.run(["curl", "-s", "--max-time", "45", "-H", f"User-Agent: {UA}", url],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", creationflags=NO_WINDOW)
    if p.returncode != 0 or not p.stdout:
        return None, f"curl rc={p.returncode}"
    try:
        doc = json.loads(p.stdout)
    except Exception as exc:
        return None, f"unparseable response: {exc}"
    msg = doc.get("message")
    if not isinstance(msg, dict):
        return None, "no Crossref record for this DOI"
    raw = msg.get("author") or []
    if not raw:
        return None, "Crossref record carries no author list"
    out = []
    for a in raw:
        if not isinstance(a, dict):
            return None, "malformed Crossref author entry"
        out.append({
            "given": (a.get("given") or "").strip(),
            "family": (a.get("family") or "").strip(),
            "orcid": (a.get("ORCID") or "").strip(),
            "sequence": (a.get("sequence") or "").strip(),
        })
    return out, "ok"


def datacite_authors(doi: str) -> tuple[list[dict] | None, str]:
    """Fallback for DOIs Crossref does not index -- arXiv registers with DataCite.

    DataCite spells creators as "Family, Given" in ``name`` and also carries
    separate ``givenName``/``familyName``, so prefer those and fall back to
    splitting ``name`` on the comma.
    """
    url = f"https://api.datacite.org/dois/{urllib.parse.quote(doi)}"
    p = subprocess.run(["curl", "-s", "-w", "\nHTTP=%{http_code}", "--max-time", "45",
                        "-H", f"User-Agent: {UA}", url],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", creationflags=NO_WINDOW)
    raw = p.stdout or ""
    code = raw.rsplit("HTTP=", 1)[-1].strip()
    body = raw.rsplit("\nHTTP=", 1)[0]
    if code != "200":
        return None, f"DataCite HTTP {code or '?'}"
    try:
        doc = json.loads(body)
    except Exception as exc:
        return None, f"unparseable DataCite response: {exc}"
    creators = ((doc.get("data") or {}).get("attributes") or {}).get("creators") or []
    if not creators:
        return None, "DataCite record carries no creator list"
    out = []
    for c in creators:
        if not isinstance(c, dict):
            return None, "malformed DataCite creator entry"
        given = (c.get("givenName") or "").strip()
        family = (c.get("familyName") or "").strip()
        if not (given or family):
            full = (c.get("name") or "").strip()
            if "," in full:
                family, _, given = full.partition(",")
                family, given = family.strip(), given.strip()
            else:
                parts = full.rsplit(" ", 1)
                given = parts[0] if len(parts) == 2 else full
                family = parts[1] if len(parts) == 2 else ""
        out.append({"given": given, "family": family,
                    "orcid": (c.get("nameIdentifiers") or [{}])[0].get("nameIdentifier", "")
                    if c.get("nameIdentifiers") else "",
                    "sequence": ""})
    return out or None, "ok"


def publisher_authors(doi: str) -> tuple[list[dict] | None, str, str]:
    """Fetch a publisher author list, Crossref first then DataCite.

    Returns (authors, source, reason). Crossref covers journal/conference DOIs;
    arXiv preprints register with DataCite instead and 404 on Crossref, so the
    fallback is what makes the recent preprint records harvestable.
    """
    authors, why = crossref_authors(doi)
    if authors:
        return authors, "crossref", why
    dc, dc_why = datacite_authors(doi)
    if dc:
        return dc, "datacite", dc_why
    return None, "", f"Crossref: {why}; DataCite: {dc_why}"


def read_record(path: Path) -> tuple[dict, str]:
    """Load publication.yaml, quoting bare ``?`` placeholders (PyYAML trap).

    Read with ``newline=""`` so the file's own line endings are preserved in the
    returned text. The default universal-newline mode would silently translate
    CRLF to LF, and writing that back would convert the whole file -- an
    unrelated change that shows up as a full-file diff.

    ``open()`` rather than ``Path.read_text()``: the latter only accepts
    ``newline`` from Python 3.13, and this runs on 3.12.
    """
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    fixed = re.sub(r'(?m)^(\s*source:\s*)\?+\s*$', r'\1"?"', text)
    doc = yaml.safe_load(fixed)
    return (doc if isinstance(doc, dict) else {}), text


def dominant_newline(text: str) -> str:
    """The line ending a file predominantly uses, so inserted lines match it."""
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    return "\r\n" if crlf > lf else "\n"


def render_mapping_block(data: dict, indent: int = 2, newline: str = "\n") -> str:
    """Render a mapping as indented YAML lines (no top-level key)."""
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False,
                          width=100, default_flow_style=False)
    pad = " " * indent
    return "".join(pad + line + newline for line in body.split("\n") if line != "")


HARVEST_KEYS = ("authors", "authors_source", "authors_fetched")


def replace_citation_block(original: str, cite: dict) -> str:
    """Add the harvested keys to a record's ``citation:`` block, touching nothing else.

    A full YAML round-trip would reformat the whole record: it re-quotes scalars
    that were quoted by hand (``issue: 'S2'`` -> ``issue: S2``), destroys every
    comment, and can silently change a value's YAML type. These files carry
    hand-written provenance comments (for example the evidence note above
    ``identifiers.repo_url`` in the BiB 2023 review record), so the edit is
    deliberately surgical:

      * existing lines outside the harvested keys are reproduced byte-for-byte;
      * only ``authors`` / ``authors_source`` / ``authors_fetched`` are written;
      * a pre-existing harvested key is replaced in place, so re-running is a
        no-op rather than a duplicate.
    """
    harvested = {k: cite[k] for k in HARVEST_KEYS if k in cite}
    if not harvested:
        return original
    # Inserted lines must use the file's own line ending, otherwise a CRLF file
    # becomes mixed and git shows a full-file diff.
    nl = dominant_newline(original)
    lines = original.splitlines(keepends=True)

    def ends_nl(s: str) -> str:
        return s if s.endswith("\n") else s + nl

    start = None
    for i, line in enumerate(lines):
        if re.match(r"^citation:\s*(#.*)?$", line.rstrip("\r\n")):
            start = i
            break

    if start is None:
        # No citation block yet: append one, separated by a blank line the way
        # the existing records do.
        tail = ends_nl(original.rstrip("\r\n"))
        return tail + nl + "citation:" + nl + render_mapping_block(harvested, newline=nl)

    # The block runs until the next top-level key (a line starting in column 0
    # that is not a comment) or EOF.
    end = len(lines)
    for j in range(start + 1, len(lines)):
        stripped = lines[j].rstrip("\r\n")
        if stripped and not stripped[0].isspace() and not stripped.lstrip().startswith("#"):
            end = j
            break

    block = lines[start + 1:end]
    # Strip every previously harvested key (with its continuation lines) so the
    # new values can be re-appended in a canonical position. Non-harvested keys
    # are reproduced byte-for-byte, which is what keeps the file's own quoting
    # and formatting intact.
    kept, i = [], 0
    while i < len(block):
        line = block[i]
        m = re.match(r"^(\s*)([A-Za-z_][\w\-]*)\s*:", line)
        if m and m.group(2) in harvested:
            indent = len(m.group(1))
            i += 1
            while i < len(block):
                nxt = block[i]
                # Stop at a blank line: PyYAML never emits one inside a block
                # sequence or nested mapping, so a blank belongs to the file's
                # own spacing, not to this key's value. Skipping it here would
                # eat the separator before the next top-level key and make the
                # edit non-idempotent.
                if not nxt.strip():
                    break
                nxt_indent = len(nxt) - len(nxt.lstrip())
                # Continuations are either more-indented (a nested mapping) or a
                # block-sequence item at the SAME indent as the key: PyYAML
                # renders `authors:\n- index: 0` flush, so an `indent > key`
                # test alone would leave the list items behind as orphans and
                # produce unparseable YAML.
                if nxt_indent > indent:
                    i += 1
                    continue
                if nxt_indent == indent and nxt.lstrip().startswith("- "):
                    i += 1
                    continue
                break
            continue
        kept.append(line)
        i += 1

    # Move any trailing blank lines out of the way so the harvested keys sit
    # inside the block, then put them back afterwards. Without that the blank
    # separator before the next top-level key is consumed and the diff is no
    # longer purely additive.
    trailing = []
    while kept and not kept[-1].strip():
        trailing.insert(0, kept.pop())

    new_block = "".join(kept)
    if new_block and not new_block.endswith("\n"):
        new_block += nl
    return ("".join(lines[:start + 1]) + new_block
            + render_mapping_block(harvested, newline=nl) + "".join(trailing)
            + "".join(lines[end:]))


# ------------------------------------------------------------------------ main
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true",
                    help="write citation.authors into publication.yaml (default: dry run)")
    ap.add_argument("--dry-run", action="store_true", help="report only (default)")
    ap.add_argument("--slug", action="append", default=[],
                    help="restrict to one registry folder (repeatable)")
    ap.add_argument("--sleep", type=float, default=0.15,
                    help="politeness delay between API calls (seconds)")
    args = ap.parse_args(argv)
    write = args.write and not args.dry_run

    if not PAPERS.is_dir():
        print(f"registry not found: {PAPERS}", file=sys.stderr)
        print("set LABX_WORK to the work root (e.g. D:\\work)", file=sys.stderr)
        return 2

    folders = sorted(p for p in PAPERS.iterdir() if (p / "publication.yaml").is_file())
    if args.slug:
        want = set(args.slug)
        folders = [p for p in folders if p.name in want]
        if not folders:
            print(f"no registry folder matched {sorted(want)}", file=sys.stderr)
            return 2

    # The lab roster is the authority on a member's name. Reuse the site's own
    # guarded lookup (name_key plus the uniqueness-gated initials index) so the
    # identity logic lives in exactly one place and this harvest cannot link a
    # person the generator would not link.
    try:
        from gen_publications import load_roster, lookup_author, roster_lookup
        lookup = roster_lookup(load_roster())
    except Exception as exc:  # roster optional: the positional gate still applies
        lookup = {}
        print(f"note: roster unavailable ({exc}); skipping the roster guard",
              file=sys.stderr)

    print(f"registry records: {len(folders)}   mode: {'WRITE' if write else 'dry run'}")
    print(f"roster rows indexed for the identity guard: {len(lookup)}")
    harvested, skipped, unchanged = [], [], []

    for folder in folders:
        path = folder / "publication.yaml"
        doc, original = read_record(path)
        ids = doc.get("identifiers") or {}
        cite = doc.get("citation") or {}
        doi = str(ids.get("doi") or "").strip()
        if not DOI_RE.match(doi):
            # Meeting abstracts carry the DOI in the harvested citation block.
            doi = str(cite.get("api_doi") or "").strip()
        if not DOI_RE.match(doi):
            skipped.append((folder.name, "no usable DOI", ""))
            continue

        reg_names = [str(a.get("name_en") or "").strip()
                     for a in (doc.get("authors") or []) if isinstance(a, dict)]
        reg_names = [n for n in reg_names if n]
        # Index of each NAMED registry author, so the harvested payload stays
        # PARALLEL to the registry author list: citation.authors[i] is the
        # publisher record for authors[reg_rows[i][0]]. An unnamed placeholder
        # row gets no entry, so its index must be tracked explicitly.
        reg_rows = [(i, a) for i, a in enumerate(doc.get("authors") or [])
                    if isinstance(a, dict) and str(a.get("name_en") or "").strip()]

        # Map each registry author string to the roster's authoritative name_en
        # when the site's guarded lookup resolves it to a lab member.
        roster_of: dict[str, str] = {}
        if lookup:
            for a in (doc.get("authors") or []):
                if not isinstance(a, dict):
                    continue
                nm = str(a.get("name_en") or "").strip()
                if not nm:
                    continue
                row = lookup_author(nm, str(a.get("name_zh") or "").strip(), lookup)
                if row and row.get("name_en"):
                    roster_of[nm] = strip_honorific(str(row["name_en"]))

        pub_authors, source, why = publisher_authors(doi)
        time.sleep(args.sleep)
        if not pub_authors:
            skipped.append((folder.name, why, doi))
            continue

        matched, reason = align(reg_names, pub_authors, roster_of=roster_of)
        if matched is None:
            skipped.append((folder.name, f"NOT ALIGNED - {reason}", doi))
            continue

        # One entry per NAMED registry author, in registry order, carrying that
        # author's index so the consumer can pair it with authors[] even when the
        # record holds unnamed placeholder rows. In subset mode `matched` is
        # already the per-registry-author pairing, not the publisher's own order.
        payload = [{"index": i, **{k: v for k, v in a.items() if v}}
                   for (i, _), a in zip(reg_rows, matched)]
        # Idempotence covers the source too: a record previously harvested from
        # Crossref that now resolves via DataCite is a real change, not a no-op.
        if cite.get("authors") == payload and cite.get("authors_source") == source:
            unchanged.append(folder.name)
            continue

        if not isinstance(cite, dict):
            cite = {}
        cite["authors"] = payload
        cite["authors_source"] = source
        cite["authors_fetched"] = _dt.date.today().isoformat()
        doc["citation"] = cite
        harvested.append((folder.name, doi, reason, reg_names, payload, source))

        if write:
            # Surgical splice, not a YAML round-trip: these records carry
            # hand-written provenance comments that a round-trip would destroy.
            path.write_text(replace_citation_block(original, cite),
                            encoding="utf-8", newline="")

    print(f"\n=== harvestable (alignment gate passed): {len(harvested)} ===")
    by_source: dict[str, int] = {}
    for name, doi, reason, reg, payload, source in harvested:
        by_source[source] = by_source.get(source, 0) + 1
    print(f"   by source: {by_source}")
    for name, doi, reason, reg, payload, source in harvested:
        print(f"\n  {name}  [{source}: {reason}]")
        for r, a in list(zip(reg, payload))[:10]:
            disp = display_name(a.get("given", ""), a.get("family", ""))
            mark = "" if r == disp else "   <-- normalized"
            print(f"      {r:24} -> {disp:26}{mark}")
        if len(reg) > 10:
            print(f"      ... and {len(reg) - 10} more")

    print(f"\n=== already up to date: {len(unchanged)} ===")
    print(f"\n=== skipped (never written): {len(skipped)} ===")
    buckets: dict[str, list[str]] = {}
    for name, reason, _doi in skipped:
        key = reason.split(" - ")[0] if " - " in reason else reason
        buckets.setdefault(key, []).append(f"{name}: {reason}")
    for key in sorted(buckets, key=lambda k: -len(buckets[k])):
        print(f"\n  --- {key}: {len(buckets[key])} ---")
        for line in buckets[key][:12]:
            print(f"      {line[:150]}")
        if len(buckets[key]) > 12:
            print(f"      ... and {len(buckets[key]) - 12} more")

    print(f"\n{'WROTE' if write else 'DRY RUN - would write'} {len(harvested)} record(s); "
          f"{len(unchanged)} already current; {len(skipped)} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
