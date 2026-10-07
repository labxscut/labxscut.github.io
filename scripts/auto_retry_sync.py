#!/usr/bin/env python3
"""Retry the tool-docs sync/push pipeline on a fixed interval until it is clean.

GitHub pushes from this host intermittently fail with `remote: Internal Server
Error` (see roles/agent_deploy/memory/LEARNED.md). This driver makes publishing
self-healing: every interval it re-runs the per-tool syncs, commits any result,
pushes, and verifies that origin/main matches the local HEAD. It exits as soon as
everything is clean and pushed, or after --attempts tries.

Usage:
    python scripts/auto_retry_sync.py [--interval-minutes 10] [--attempts 6]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parents[1]
TOOLS = ("sxLaep", "sxSNF", "deeplb")
TRAILER = "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"


def log(message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{stamp}] {message}", flush=True)


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(SITE_ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result


def remote_main() -> str:
    result = git("ls-remote", "origin", "refs/heads/main", check=False)
    if result.returncode or not result.stdout.strip():
        return ""
    return result.stdout.split()[0]


def run_sync(tool: str) -> bool:
    result = subprocess.run(
        [sys.executable, str(SITE_ROOT / "scripts" / "sync_tool_docs.py"), "--tool", tool],
        cwd=SITE_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = ((result.stdout or "") + (result.stderr or "")).strip()
    if output:
        log(f"sync {tool}: {output.splitlines()[-1]}")
    return result.returncode == 0


def commit_changes() -> bool:
    git("add", "tools", "_data/tools.yml")
    staged = git("diff", "--cached", "--name-only").stdout.strip()
    if not staged:
        return False
    message = (
        "Sync tool docs from repository source of truth\n\n"
        "Refreshed by scripts/auto_retry_sync.py.\n\n" + TRAILER
    )
    git("commit", "-m", message)
    log("committed synced pages")
    return True


def push_and_verify() -> bool:
    result = git("push", "origin", "HEAD:refs/heads/main", check=False)
    detail = ((result.stdout or "") + (result.stderr or "")).strip()
    if detail:
        log(f"push: {detail.splitlines()[-1]}")
    if result.returncode:
        return False
    head = git("rev-parse", "HEAD").stdout.strip()
    for _ in range(3):
        if remote_main() == head:
            log(f"verified origin/main == {head[:12]}")
            return True
        time.sleep(5)
    log(f"push accepted but origin/main still {remote_main()[:12]}")
    return False


def one_pass() -> bool:
    """Return True when the site is synced and published."""
    for tool in TOOLS:
        if not run_sync(tool):
            log(f"sync failed for {tool}; will retry next interval")
            return False
    commit_changes()
    if not push_and_verify():
        log("push not verified; will retry next interval")
        return False
    dirty = git("status", "--porcelain", "tools", "_data/tools.yml").stdout.strip()
    if dirty:
        log(f"unexpected local changes: {dirty.splitlines()[0]}")
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval-minutes", type=float, default=10.0)
    parser.add_argument("--attempts", type=int, default=6)
    args = parser.parse_args()

    for attempt in range(1, args.attempts + 1):
        log(f"attempt {attempt}/{args.attempts}")
        try:
            if one_pass():
                log("pipeline clean and published; stopping")
                return 0
        except Exception as error:  # retry loop must survive any failure
            log(f"error: {error}")
        if attempt < args.attempts:
            log(f"sleeping {args.interval_minutes:g} min")
            time.sleep(args.interval_minutes * 60)
    log("gave up after all attempts")
    return 1


if __name__ == "__main__":
    sys.exit(main())
