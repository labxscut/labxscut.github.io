#!/usr/bin/env python3
"""Verify tool-repo remote state, then run the explicit docs sync for each tool.

This is a thin OS-operations driver: it shells out to git and to
sync_tool_docs.py, reports what it finds, and stops on the first failure so
the caller sees one clear error instead of a cascade.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = SITE_ROOT.parent
SYNC = SITE_ROOT / "scripts" / "sync_tool_docs.py"
TOOLS = ("sxLaep", "sxSNF", "DeepLB")
# Keys accepted by sync_tool_docs.py --tool, in the same order as TOOLS.
SYNC_KEYS = ("sxLaep", "sxSNF", "deeplb")

# Console-subsystem children (git.exe) get a new visible console when the
# parent has none, e.g. under pythonw.exe. CREATE_NO_WINDOW is Windows-only.
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=NO_WINDOW,
    )


def fail(message: str) -> "SystemExit":
    print(f"FAIL: {message}")
    raise SystemExit(1)


def check_remotes() -> None:
    print("== remote branch state ==")
    for name in TOOLS:
        repo = SOURCE_ROOT / name
        result = run(["git", "-C", str(repo), "ls-remote", "origin",
                      "refs/heads/main", "refs/heads/release"])
        if result.returncode:
            fail(f"ls-remote {name}: {result.stderr.strip()}")
        refs = {}
        for line in result.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) == 2:
                refs[parts[1]] = parts[0][:12]
        for branch in ("main", "release"):
            key = f"refs/heads/{branch}"
            print(f"  {name:8s} {branch:8s} {refs.get(key, 'MISSING')}")
        if "refs/heads/release" not in refs:
            fail(f"{name} has no origin/release branch")


def check_local_clean() -> None:
    print("== local worktree state ==")
    for name in TOOLS:
        repo = SOURCE_ROOT / name
        result = run(["git", "-C", str(repo), "status", "--porcelain"])
        if result.returncode:
            fail(f"status {name}: {result.stderr.strip()}")
        dirty = result.stdout.strip()
        print(f"  {name:8s} {'CLEAN' if not dirty else 'DIRTY: ' + dirty}")
    site = run(["git", "-C", str(SITE_ROOT), "status", "--porcelain"])
    dirty = site.stdout.strip()
    print(f"  {'site':8s} {'CLEAN' if not dirty else 'DIRTY: ' + dirty}")


def run_syncs() -> None:
    print("== sync ==")
    for name, key in zip(TOOLS, SYNC_KEYS):
        print(f"-- {key} --")
        result = run([sys.executable, str(SYNC), "--tool", key], cwd=SITE_ROOT)
        print(result.stdout.rstrip())
        if result.stderr.strip():
            print(result.stderr.rstrip())
        if result.returncode:
            fail(f"sync {key} exited {result.returncode}")


def show_site_diff() -> None:
    print("== website changes after sync ==")
    result = run(["git", "-C", str(SITE_ROOT), "status", "--porcelain"])
    print(result.stdout.rstrip() or "(nothing changed)")
    diff = run(["git", "-C", str(SITE_ROOT), "diff", "--", "_data/tools.yml"])
    print(diff.stdout.rstrip() or "(no tools.yml diff)")


def main() -> int:
    check_remotes()
    check_local_clean()
    run_syncs()
    show_site_diff()
    print("== done ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
