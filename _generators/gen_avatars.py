#!/usr/bin/env python3
"""Generate cartoon profile-photo placeholders for team members.

Each member gets a deterministic, friendly bust illustration under
``images/avatars/<nick>.svg`` so the profile card always shows the same
picture for the same person.  The artwork is generated from the roster nick
only (no personal data), so it is safe to publish and can be replaced later
by a real portrait dropped in at the same path.

Usage (WSL):  python3 _generators/gen_avatars.py lcx cxy ...
Usage:        from gen_avatars import ensure_avatar
"""
from __future__ import annotations

import hashlib
import sys

from gen_publications import REPO

AVATAR_DIR = REPO / "images" / "avatars"
AVATAR_ROOT = "/images/avatars"

# Skin/hair tones kept deliberately muted so any hue-tinted background works.
SKIN_TONES = ("#f2c9a0", "#e8b088", "#d89a6c", "#c3855c", "#a9714b", "#f7d7bd")
HAIR_TONES = ("#3a3038", "#4d3b2e", "#26221f", "#5b4a3c", "#6f5b4a", "#2f2a33")
GOWN_TONES = ("#4a5578", "#3f6b5e", "#6d4f63", "#5d6355", "#6b5a45", "#46607a")


def digest(nick: str) -> bytes:
    return hashlib.sha256(nick.encode("utf-8")).digest()


def palette(nick: str) -> dict[str, object]:
    """Pick a deterministic palette and shape set for one member."""
    raw = digest(nick)
    hue = raw[0] * 360 // 255
    return {
        "bg": f"hsl({hue}, 42%, 84%)",
        "bg_deep": f"hsl({hue}, 38%, 70%)",
        "skin": SKIN_TONES[raw[1] % len(SKIN_TONES)],
        "hair": HAIR_TONES[raw[2] % len(HAIR_TONES)],
        "gown": GOWN_TONES[raw[3] % len(GOWN_TONES)],
        "glasses": bool(raw[4] % 3 == 0),
        "bangs": raw[5] % 3,
        "smile": 6 + (raw[6] % 4),
    }


def svg(nick: str) -> str:
    c = palette(nick)
    assert isinstance(c["bg"], str)
    bangs = {
        # three simple fringe shapes sharing the same head circle
        0: '<path d="M52 62c4-22 52-24 56-2 3 12-8 8-14 4-9-6-20-6-28 0-6 4-17 8-14-2z"/>',
        1: '<path d="M50 64c2-24 58-24 60 0 1 9-9 6-13 0-8-11-26-11-34 0-4 6-12 9-13 0z"/>',
        2: '<path d="M51 66c-2-26 60-26 58 0-1 8-11 4-14-3-7-14-24-14-31 0-3 7-12 11-13 3z"/>',
    }[int(c["bangs"])]
    glasses = ""
    if c["glasses"]:
        glasses = (
            '<g fill="none" stroke="#3a3a45" stroke-width="2.6" opacity="0.85">'
            '<circle cx="68" cy="84" r="10"/>'
            '<circle cx="92" cy="84" r="10"/>'
            '<path d="M78 84h4M58 82l-6-3M102 82l6-3"/>'
            "</g>"
        )
    smile = float(c["smile"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160" role="img" aria-label="Cartoon placeholder portrait">
  <defs>
    <clipPath id="frame"><circle cx="80" cy="80" r="78"/></clipPath>
  </defs>
  <g clip-path="url(#frame)">
    <rect width="160" height="160" fill="{c["bg"]}"/>
    <circle cx="80" cy="150" r="62" fill="{c["gown"]}"/>
    <path d="M62 118h36v20H62z" fill="{c["skin"]}"/>
    <circle cx="80" cy="86" r="34" fill="{c["skin"]}"/>
    <g fill="{c["hair"]}">{bangs}</g>
    <g fill="#33302f">
      <circle cx="69" cy="88" r="3.4"/>
      <circle cx="91" cy="88" r="3.4"/>
    </g>
    <path d="M70 102q10 {smile} 20 0" fill="none" stroke="#8a5a4a" stroke-width="3" stroke-linecap="round"/>
    {glasses}
  </g>
  <circle cx="80" cy="80" r="78" fill="none" stroke="{c["bg_deep"]}" stroke-width="3"/>
</svg>
"""


def ensure_avatar(nick: str) -> str:
    """Write the placeholder for ``nick`` if missing and return its site path."""
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    path = AVATAR_DIR / f"{nick}.svg"
    if not path.exists():
        path.write_text(svg(nick), encoding="utf-8")
    return f"{AVATAR_ROOT}/{path.name}"


def main(argv: list[str]) -> int:
    nicks = argv[1:] or []
    if not nicks:
        print("usage: gen_avatars.py <nick> [<nick> ...]")
        return 1
    for nick in nicks:
        print(ensure_avatar(nick))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
