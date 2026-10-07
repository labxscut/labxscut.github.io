#!/usr/bin/env python3
"""Generate deterministic tool logos and mirror them into the tool catalog.

Each LabX tool gets a flat, self-contained SVG badge at
``images/tools/<key>.svg`` derived only from the tool key, so the artwork is
stable across runs and safe to publish.  The generator also records the path in
the ``logo:`` field of the matching ``_data/tools.yml`` entry.

An existing file is never overwritten: a hand-drawn logo dropped at the same
path wins permanently.  The same artwork is published to the tool repository
(see ``--print`` output / scripts/publish_tool_logos.py) so
``github.com/labxscut/<tool>`` carries its own logo.

Usage:  python3 _generators/gen_tool_logos.py [--dry-run]
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import yaml

from gen_publications import REPO

LOGO_DIR = REPO / "images" / "tools"
LOGO_ROOT = "/images/tools"
TOOLS_DATA = REPO / "_data" / "tools.yml"

# Muted, print-friendly palettes; hue is chosen from the tool key.
HUES = range(0, 360, 15)


def digest(key: str) -> bytes:
    return hashlib.sha256(key.encode("utf-8")).digest()


def palette(key: str) -> dict[str, object]:
    raw = digest(key)
    hue = HUES[raw[0] % len(HUES)]
    return {
        "hue": hue,
        "light": f"hsl({hue}, 62%, 72%)",
        "deep": f"hsl({(hue + 28) % 360}, 55%, 34%)",
        "ring": f"hsl({(hue + 180) % 360}, 45%, 40%)",
        # three glyph motifs: node cluster, layered bars, hex outline
        "motif": raw[1] % 3,
    }


def motif(p: dict[str, object]) -> str:
    shapes = {
        0: (
            '<circle cx="44" cy="52" r="9" fill="#ffffff" opacity="0.92"/>'
            '<circle cx="84" cy="40" r="7" fill="#ffffff" opacity="0.75"/>'
            '<circle cx="80" cy="82" r="11" fill="#ffffff" opacity="0.92"/>'
            '<path d="M44 52 84 40M44 52 80 82M84 40 80 82" stroke="#ffffff"'
            ' stroke-width="4" stroke-linecap="round" opacity="0.65"/>'
        ),
        1: (
            '<rect x="34" y="70" width="60" height="12" rx="6" fill="#ffffff" opacity="0.92"/>'
            '<rect x="42" y="50" width="44" height="12" rx="6" fill="#ffffff" opacity="0.72"/>'
            '<rect x="50" y="30" width="28" height="12" rx="6" fill="#ffffff" opacity="0.52"/>'
        ),
        2: (
            '<path d="M64 26 96 45v42L64 106 32 87V45z" fill="none" stroke="#ffffff"'
            ' stroke-width="7" stroke-linejoin="round" opacity="0.9"/>'
            '<circle cx="64" cy="66" r="10" fill="#ffffff" opacity="0.85"/>'
        ),
    }
    return shapes[int(p["motif"])]


def svg(key: str) -> str:
    p = palette(key)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-label="{key} logo">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{p["light"]}"/>
      <stop offset="1" stop-color="{p["deep"]}"/>
    </linearGradient>
    <clipPath id="frame"><rect x="4" y="4" width="120" height="120" rx="28"/></clipPath>
  </defs>
  <rect x="4" y="4" width="120" height="120" rx="28" fill="url(#bg)"/>
  <g clip-path="url(#frame)">
    {motif(p)}
  </g>
  <rect x="4" y="4" width="120" height="120" rx="28" fill="none" stroke="{p["ring"]}" stroke-width="2" opacity="0.5"/>
</svg>
"""


def logo_svg(key: str) -> str:
    """Logo markup for ``key``; a hand-drawn file at the site path wins."""
    path = LOGO_DIR / f"{key}.svg"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return svg(key)


def ensure_logo(key: str) -> str:
    """Write the logo for ``key`` if missing and return its site path."""
    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    path = LOGO_DIR / f"{key}.svg"
    if not path.exists():
        path.write_text(svg(key), encoding="utf-8", newline="\n")
    return f"{LOGO_ROOT}/{path.name}"


def catalog_keys(text: str) -> list[tuple[str, int, int]]:
    """Return (key, block start, block end) for every entry in tools.yml."""
    starts = [m.start() for m in re.finditer(r"(?m)^- key: ([^\r\n]+)\r?$", text)]
    out = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        key = re.match(r"^- key: ([^\r\n]+)", text[start:end]).group(1).strip()
        out.append((key, start, end))
    return out


def add_logo_field(text: str, paths: dict[str, str]) -> tuple[str, int]:
    """Insert a ``logo:`` line after ``name:`` for entries that lack one."""
    insertions = []
    for key, start, end in catalog_keys(text):
        block = text[start:end]
        if re.search(r"(?m)^  logo:", block):
            continue
        lines = block.splitlines(keepends=True)
        target = next(
            (i for i, line in enumerate(lines) if line.startswith("  name:")),
            1,
        )
        lines.insert(target + 1, f"  logo: {paths[key]}\n")
        insertions.append((start, end, "".join(lines)))
    for start, end, replacement in reversed(insertions):
        text = text[:start] + replacement + text[end:]
    return text, len(insertions)


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    tools = yaml.safe_load(TOOLS_DATA.read_text(encoding="utf-8"))
    paths: dict[str, str] = {}
    for tool in tools:
        key = tool["key"]
        paths[key] = ensure_logo(key)
        print(f"{key}: {paths[key]}")

    if dry_run:
        return 0

    text = TOOLS_DATA.read_text(encoding="utf-8")
    updated, added = add_logo_field(text, paths)
    if added:
        TOOLS_DATA.write_text(updated, encoding="utf-8", newline="")
    print(f"logos: {len(paths)} files, tools.yml entries updated: {added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
