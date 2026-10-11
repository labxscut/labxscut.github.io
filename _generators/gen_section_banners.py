#!/usr/bin/env python3
"""Generate the section title banners at images/banners/<section>.svg.

Each nav section gets a wide, flat "techno" motif that sits above its title
(see _includes/section-banner.html).  The artwork is derived only from the
section key and a fixed palette, so it is deterministic across runs and safe
to publish.  An existing file is never overwritten: a hand-drawn banner at the
same path wins permanently.

Usage:  python3 _generators/gen_section_banners.py [--dry-run]
"""
from __future__ import annotations

import sys
from pathlib import Path

from gen_publications import REPO

BANNER_DIR = REPO / "images" / "banners"

# Section -> motif. Order mirrors the navigation (0design/README.md).
SECTIONS = [
    ("news", "timeline"),
    ("about", "graph"),
    ("team", "cluster"),
    ("tools", "hexcircuit"),
    ("publications", "layers"),
    ("activities", "waveform"),
    ("engage", "signal"),
]

W, H = 1200, 150

# Lab palette (matches images/hero.svg): deep blues with three accents.
BG = "#0d2746"
GRID = "#1b3b60"
STRAND = "#4aa3d8"
BRIGHT = "#79b9ff"
AMBER = "#f2b134"
GREEN = "#58c26a"
PURPLE = "#d678c8"


def frame(inner: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" role="img" aria-hidden="true">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <g stroke="{GRID}" stroke-width="1" opacity="0.7">
    <line x1="0" y1="30" x2="{W}" y2="30"/>
    <line x1="0" y1="75" x2="{W}" y2="75"/>
    <line x1="0" y1="120" x2="{W}" y2="120"/>
  </g>
  {inner}
</svg>
"""


def timeline() -> str:
    # a date axis with event nodes - lab news
    dots = []
    for i, x in enumerate(range(90, W - 60, 120)):
        accent = (AMBER, GREEN, PURPLE, BRIGHT)[i % 4]
        r = 9 if i % 3 == 0 else 6
        dots.append(f'<circle cx="{x}" cy="75" r="{r}" fill="{accent}"/>')
        dots.append(f'<line x1="{x}" y1="75" x2="{x}" y2="{20 + (i % 3) * 22}" stroke="{BRIGHT}" stroke-width="2" opacity="0.55"/>')
    return (
        f'<line x1="40" y1="75" x2="{W - 40}" y2="75" stroke="{STRAND}" stroke-width="4" stroke-linecap="round"/>'
        + "".join(dots)
    )


def graph() -> str:
    # connected knowledge nodes - research themes
    nodes = [(120, 55), (300, 105), (470, 45), (650, 95), (830, 50), (1010, 100), (1120, 60)]
    edges = "".join(
        f'<line x1="{nodes[i][0]}" y1="{nodes[i][1]}" x2="{nodes[i + 1][0]}" y2="{nodes[i + 1][1]}" stroke="{BRIGHT}" stroke-width="2.5" opacity="0.6"/>'
        for i in range(len(nodes) - 1)
    )
    edge2 = f'<line x1="{nodes[0][0]}" y1="{nodes[0][1]}" x2="{nodes[2][0]}" y2="{nodes[2][1]}" stroke="{STRAND}" stroke-width="2" opacity="0.45"/>'
    circles = "".join(
        f'<circle cx="{x}" cy="{y}" r="{10 if i % 2 == 0 else 7}" fill="{[AMBER, BRIGHT, GREEN, PURPLE][i % 4]}"/>'
        for i, (x, y) in enumerate(nodes)
    )
    return edges + edge2 + circles


def cluster() -> str:
    # one hub with member nodes around it - the team
    hub = (W // 2, 75)
    spokes = []
    for i in range(9):
        ang = i * 40
        import math
        x = hub[0] + int(230 * math.cos(math.radians(ang)))
        y = 75 + int(48 * math.sin(math.radians(ang)))
        accent = [BRIGHT, AMBER, GREEN, PURPLE][i % 4]
        spokes.append(
            f'<line x1="{hub[0]}" y1="{hub[1]}" x2="{x}" y2="{y}" stroke="{STRAND}" stroke-width="2" opacity="0.5"/>'
            f'<circle cx="{x}" cy="{y}" r="8" fill="{accent}"/>'
        )
    return (
        "".join(spokes)
        + f'<circle cx="{hub[0]}" cy="{hub[1]}" r="18" fill="{BRIGHT}"/>'
        + f'<circle cx="{hub[0]}" cy="{hub[1]}" r="26" fill="none" stroke="{BRIGHT}" stroke-width="2" opacity="0.45"/>'
    )


def hexcircuit() -> str:
    # a row of hex cells with circuit leads - software tools
    cells = []
    for i, cx in enumerate(range(110, W - 60, 150)):
        cy = 75
        s = 34
        pts = " ".join(
            f"{cx + int(s * __import__('math').cos(__import__('math').radians(a)))},"
            f"{cy + int(s * __import__('math').sin(__import__('math').radians(a)))}"
            for a in range(30, 361, 60)
        )
        accent = [BRIGHT, GREEN, AMBER, PURPLE][i % 4]
        cells.append(
            f'<polygon points="{pts}" fill="none" stroke="{accent}" stroke-width="3" opacity="0.9"/>'
            f'<circle cx="{cx}" cy="{cy}" r="6" fill="{accent}"/>'
            f'<line x1="{cx + s}" y1="{cy}" x2="{cx + s + 40}" y2="{cy}" stroke="{STRAND}" stroke-width="2" opacity="0.6"/>'
        )
    return "".join(cells)


def layers() -> str:
    # stacked sheets - the publication record (kept inside the 150px canvas)
    sheets = []
    for i in range(5):
        y = 26 + i * 14
        x = 140 + i * 130
        accent = [BRIGHT, STRAND, GREEN, AMBER, PURPLE][i % 5]
        sheets.append(
            f'<rect x="{x}" y="{y}" width="150" height="60" rx="10" fill="none" stroke="{accent}" stroke-width="3" opacity="{0.9 - i * 0.1}"/>'
            f'<line x1="{x + 18}" y1="{y + 22}" x2="{x + 132}" y2="{y + 22}" stroke="{accent}" stroke-width="2" opacity="0.5"/>'
            f'<line x1="{x + 18}" y1="{y + 38}" x2="{x + 104}" y2="{y + 38}" stroke="{accent}" stroke-width="2" opacity="0.4"/>'
        )
    return "".join(sheets)


def waveform() -> str:
    # activity bars along a baseline - events and meetings
    bars = []
    for i, x in enumerate(range(70, W - 40, 46)):
        import math
        hgt = int(38 + 26 * math.sin(math.radians(i * 33)))
        accent = [BRIGHT, AMBER][i % 2]
        bars.append(
            f'<rect x="{x}" y="{75 - hgt}" width="16" height="{hgt * 2}" rx="6" fill="{accent}" opacity="{0.55 + (i % 3) * 0.15}"/>'
        )
    return "".join(bars)


def signal() -> str:
    # radiating arcs from a sending node - outreach and contact
    cx, cy = 200, 75
    arcs = "".join(
        f'<path d="M{cx} {cy} m{r} 0 a{r} {r} 0 0 1 {int(r * 0.7)} {int(r * 0.7)}" fill="none" stroke="{BRIGHT}" stroke-width="3" opacity="{0.85 - i * 0.15}"/>'
        for i, r in enumerate((40, 78, 116, 154))
    )
    return (
        f'<circle cx="{cx}" cy="{cy}" r="14" fill="{AMBER}"/>'
        + arcs
        + f'<line x1="{cx + 170}" y1="75" x2="{W - 90}" y2="75" stroke="{STRAND}" stroke-width="2" stroke-dasharray="10 8" opacity="0.6"/>'
        + f'<circle cx="{W - 80}" cy="75" r="10" fill="{GREEN}"/>'
    )


MOTIFS = {
    "timeline": timeline,
    "graph": graph,
    "cluster": cluster,
    "hexcircuit": hexcircuit,
    "layers": layers,
    "waveform": waveform,
    "signal": signal,
}


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    BANNER_DIR.mkdir(parents=True, exist_ok=True)
    for key, motif in SECTIONS:
        path = BANNER_DIR / f"{key}.svg"
        if path.exists():
            print(f"{key}: kept existing {path.name}")
            continue
        svg = frame(MOTIFS[motif]())
        if dry_run:
            print(f"{key}: would write {path.name}")
            continue
        path.write_text(svg, encoding="utf-8", newline="\n")
        print(f"{key}: wrote {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
