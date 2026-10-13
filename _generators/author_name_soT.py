#!/usr/bin/env python3
"""Resolve the canonical author-name module from the shared backend library.

Author-name formats have exactly ONE implementation, in the shared backend
library ``agents/hermes/lib/author_name.py`` (SOP:
``agents/sop/labxscut-backend-specs.md`` § Author names). The site generators
import it from there rather than carrying a copy, because a second copy is how
the site and the registry drift apart -- the defect this exists to prevent.

The work tree is already a hard dependency of these generators (the registry
lives at ``advisee/hc/labxManage`` and the roster at ``advisee/core/database``),
so resolving the library through ``LABX_WORK`` adds no new requirement. If it
cannot be found the import fails loudly with the fix, rather than silently
falling back to a stale local copy.

Usage:
    from author_name_soT import author_name
    author_name.display_name("Li C.", "Xia")   # -> "Li C. Xia"
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

WORK = Path(os.environ.get("LABX_WORK", "/mnt/d/work"))
LIB = WORK / "agents" / "hermes" / "lib"
MODULE_PATH = LIB / "author_name.py"

if not MODULE_PATH.is_file():
    raise ImportError(
        f"canonical author-name module not found at {MODULE_PATH}. "
        f"Set LABX_WORK to the work root (currently {WORK!r}); the shared "
        f"backend library must be present at agents/hermes/lib/author_name.py. "
        f"See agents/sop/labxscut-backend-specs.md."
    )

_spec = importlib.util.spec_from_file_location("author_name", MODULE_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise ImportError(f"cannot load {MODULE_PATH}")
author_name = importlib.util.module_from_spec(_spec)
# Make it importable by name from the library too, so the MCP wrapper and any
# sibling module resolve the same object rather than a second copy.
sys.modules.setdefault("author_name", author_name)
_spec.loader.exec_module(author_name)

__all__ = ["author_name", "MODULE_PATH"]
