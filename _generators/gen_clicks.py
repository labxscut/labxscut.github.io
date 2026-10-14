#!/usr/bin/env python3
"""Fetch GoatCounter click counts and write _data/clicks.yml.

The site is a static GitHub Pages build, so it cannot call the analytics API at
render time. This generator runs locally (never in CI, never on Pages), reads the
scoped API token from the private vault, pulls per-path counts from the
GoatCounter v0 API, folds them into tool keys and publication slugs, and commits
ONLY the derived counts in `_data/clicks.yml`. No secret ever enters the repo.

Which clicks a tool / paper gets
--------------------------------
`_scripts/goatcounter-events.js` emits three event kinds plus ordinary pageviews:

    paper:<file>.pdf        a local /papers/*.pdf was opened
    outbound:<host><path>   a link leaving the site was followed
    keyword:<term>          a topic-cloud term was clicked
    /tools/<slug>           a hosted docs page was viewed (a pageview)

A tool is credited with:
  * outbound clicks to its GitHub repository (`outbound:github.com/<owner>/<repo>`), and
  * pageviews of its docs when they are hosted on this site (`/tools/<slug>/`).
A paper is credited with:
  * `paper:<basename>` events for its local PDF, and
  * outbound DOI clicks (`outbound:doi.org/<doi>`).

Matching is case-insensitive on the host/path because the browser's URL API
lowercases the host but preserves the path, and DOIs come in mixed case.

Usage
-----
    python _generators/gen_clicks.py            # fetch and write _data/clicks.yml
    python _generators/gen_clicks.py --dry-run  # fetch and print, write nothing
    python _generators/gen_clicks.py --days 90  # only count the last 90 days

The vault token is resolved through the shared backend library (the same
`LABX_WORK` convention as `author_name_soT.py`). Run it where the vault lives
(WSL: `~/.hermes/accounts.vault.xlsx`).
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

SITE = Path(__file__).resolve().parents[1]
DATA = SITE / "_data"
WORK = Path(os.environ.get("LABX_WORK", "/mnt/d/work"))

VAULT_SERVICE = "S-GoatCounter-API"
COUNTER_CODE = "labxscut"
API_BASE = "https://%s.goatcounter.com/api/v0" % COUNTER_CODE

# How many top items get the "hot" mark. The templates only render it once the
# site crosses the enable threshold in _config.yml, so this is the shape of the
# hot list, not whether it shows.
HOT_N = 3


# --------------------------------------------------------------------------- #
# secrets: resolve the token, never print it
# --------------------------------------------------------------------------- #
def load_token() -> str:
    """Return the API token from the vault, or exit with a clear fix.

    The vault lives inside WSL's ext4 (`~/.hermes/accounts.vault.xlsx`), so the
    home directory is resolved from the *running* user rather than LABX_WORK --
    on Windows `Path.home()` points at a tree with no vault.
    """
    agents = WORK / "agents"
    sys.path.insert(0, str(agents))
    try:
        from hermes.vault_resolve import load_vault_rows  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        sys.exit(
            "cannot import the vault resolver from %s (%s).\n"
            "Run this where the vault lives (WSL: ~/.hermes/accounts.vault.xlsx) "
            "and set LABX_WORK to the work root (currently %r)." % (agents, exc, WORK)
        )
    for row in load_vault_rows():
        if (row.get("service") or "").strip() == VAULT_SERVICE:
            tok = (row.get("password") or "").strip()
            if tok:
                return tok
    sys.exit("no %s row in the vault; add the scoped API token there." % VAULT_SERVICE)


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #
def api_get(path: str, token: str) -> object:
    req = urllib.request.Request(API_BASE + path)
    # Docs: "Leave the username empty and use the API key as the password."
    req.add_header("Authorization", "Basic " + base64.b64encode((":%s" % token).encode()).decode())
    last = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                raise RuntimeError("API auth failed (HTTP %d); check the vault token." % exc.code)
            last = exc
        except Exception as exc:  # timeouts, transient 5xx
            last = exc
    raise RuntimeError("API request failed for %s: %s" % (path, last))


def fetch_hits(token: str, days: int) -> list[dict]:
    """Return the per-path hit list.

    `/api/v0/stats/hits` wants date-only (`YYYY-MM-DD`) values; the `T00:00`
    form is rejected with 400. With no `start`/`end` the API returns the whole
    history, which is the default here. `limit` is the number of paths to
    return; 1000 comfortably exceeds this counter's whole path space, and the
    response's `more` flag is checked so a future overflow fails loudly rather
    than silently undercounting.
    """
    q = "?limit=1000"
    if days:
        today = dt.date.today()
        q = "?start=%s&end=%s&limit=1000" % (
            (today - dt.timedelta(days=days)).isoformat(),
            (today + dt.timedelta(days=1)).isoformat(),
        )
    d = api_get("/stats/hits" + q, token)
    if d.get("more"):
        raise RuntimeError(
            "the counter has more than 1000 distinct paths; raise the limit and "
            "paginate with exclude_paths before trusting these totals."
        )
    return d.get("hits") or []


# --------------------------------------------------------------------------- #
# folding counts into site keys
# --------------------------------------------------------------------------- #
def load_yml(name: str):
    with open(DATA / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def build(token: str, days: int) -> dict:
    tools = load_yml("tools.yml") or []
    pubs = load_yml("publications.yml") or []

    hits = fetch_hits(token, days)

    # case-insensitive lookup tables built from the site's own data
    tool_by_path: dict[str, str] = {}   # normalised path -> tool key
    for t in tools:
        key = t.get("key")
        slug = (t.get("docs_slug") or "").strip()
        if slug:
            tool_by_path[("/tools/%s" % slug).lower()] = key
        repo = (t.get("repo") or "").strip()
        if repo:
            tail = repo.split("github.com/")[-1].strip("/").lower()
            if tail:
                tool_by_path[("outbound:github.com/" + tail)] = key

    paper_by_path: dict[str, str] = {}  # normalised path -> slug
    for p in pubs:
        slug = p.get("slug")
        pdf = (p.get("pdf") or "")
        if "papers/" in pdf:
            base = pdf.split("/")[-1].lower()
            paper_by_path["paper:" + base] = slug
        doi = (p.get("doi") or "").strip().lower()
        if doi:
            paper_by_path["outbound:doi.org/" + doi] = slug

    tool_counts: dict[str, int] = {}
    paper_counts: dict[str, int] = {}
    total_hits = 0
    total_events = 0
    for h in hits:
        path = (h.get("path") or "").strip()
        count = int(h.get("count") or 0)
        total_hits += count
        if bool(h.get("event")):
            total_events += count
        norm = path.rstrip("/").lower()
        if norm in tool_by_path:
            k = tool_by_path[norm]
            tool_counts[k] = tool_counts.get(k, 0) + count
        elif norm in paper_by_path:
            s = paper_by_path[norm]
            paper_counts[s] = paper_counts.get(s, 0) + count

    # Order keys/papers by clicks (desc, then name for a stable tie-break). Every
    # registered tool and paper appears, so the templates can sort the full grid
    # -- not just the ones with clicks -- without a second lookup.
    def rank(mapping: dict[str, int], all_keys: list[str]) -> list[str]:
        return sorted(all_keys, key=lambda k: (-mapping.get(k, 0), k.lower()))

    tool_order = rank(tool_counts, [t.get("key") for t in tools if t.get("key")])
    paper_order = rank(paper_counts, [p.get("slug") for p in pubs if p.get("slug")])

    today = dt.date.today()
    return {
        "generated": today.strftime("%Y%m%d"),
        "window_days": days,
        "totals": {"hits": total_hits, "events": total_events},
        # full popularity order (used to sort /tools/); all keys present
        "tool_order": tool_order,
        "paper_order": paper_order,
        # top-N with at least one click get the hot mark (N = --hot)
        "hot_tools": [k for k in tool_order if tool_counts.get(k, 0) > 0][: HOT_N],
        "hot_papers": [s for s in paper_order if paper_counts.get(s, 0) > 0][: HOT_N],
        # raw per-item counts for the "N clicks" label
        "counts": {
            "tools": dict(sorted(tool_counts.items())),
            "papers": dict(sorted(paper_counts.items())),
        },
    }


def render(data: dict) -> str:
    header = (
        "# Generated by _generators/gen_clicks.py -- do not hand-edit.\n"
        "# GoatCounter click counts folded into tool keys and publication slugs.\n"
        "# Counts are derived data; the API token stays in the private vault.\n"
    )
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return header + body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="print the YAML, write nothing")
    ap.add_argument("--days", type=int, default=0, help="count window in days (0 = all history)")
    ap.add_argument("--out", default=str(DATA / "clicks.yml"), help="output path (default _data/clicks.yml)")
    args = ap.parse_args()

    token = load_token()
    data = build(token, args.days)
    text = render(data)

    if args.dry_run:
        print(text)
        return 0

    out = Path(args.out)
    old = out.read_text(encoding="utf-8") if out.exists() else ""
    if old == text:
        print("UNCHANGED: %s" % out)
    else:
        out.write_text(text, encoding="utf-8")
        print("WROTE %s (hot_tools=%d, hot_papers=%d, total_hits=%d, total_events=%d)"
              % (out, len(data["hot_tools"]), len(data["hot_papers"]),
                 data["totals"]["hits"], data["totals"]["events"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
