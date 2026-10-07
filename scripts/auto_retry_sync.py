#!/usr/bin/env python3
"""Retry the tool-docs sync/push pipeline on a fixed interval until it is clean.

GitHub pushes from this host intermittently fail with `remote: Internal Server
Error`, and the WiFi here drops often enough that a manual re-run is not good
enough. This driver makes publishing self-healing: each pass re-runs the
per-tool syncs, commits any result, pushes, and verifies that origin/main
matches the local HEAD. Failures are retried after --interval-minutes; a
resident watcher (--forever) keeps re-checking so recovered connections and new
upstream docs are picked up automatically.

Usage:
    python scripts/auto_retry_sync.py                     # 6 attempts, 10 min apart
    python scripts/auto_retry_sync.py --attempts 1        # single pass (for schedulers)
    python scripts/auto_retry_sync.py --forever           # resident 10-minute watcher
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parents[1]
STATE_ROOT = SITE_ROOT.parent / "logs"
DEFAULT_LOG = STATE_ROOT / "auto_retry_sync.log"
DEFAULT_LOCK = STATE_ROOT / "auto_retry_sync.lock"
TOOLS = ("sxLaep", "sxSNF", "deeplb")
TRAILER = "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

_LOG_PATH: Path | None = None


def log(message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    try:
        print(line, flush=True)
    except (OSError, ValueError):  # pythonw has no console; the log file still works
        pass
    if _LOG_PATH is not None:
        try:
            with _LOG_PATH.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        except OSError:
            pass


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            if ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return code.value == 259  # STILL_ACTIVE
            return True
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


class Lock:
    """Single-instance guard so scheduled runs and watchers cannot overlap."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.held = False

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            owner = self.path.read_text(encoding="utf-8", errors="replace").strip()
            if owner.isdigit() and process_alive(int(owner)):
                log(f"another instance is running (pid {owner}); nothing to do")
                return False
            log(f"removing stale lock from pid {owner or 'unknown'}")
            self.path.unlink(missing_ok=True)
        self.path.write_text(str(os.getpid()), encoding="utf-8")
        self.held = True
        return True

    def release(self) -> None:
        if self.held:
            self.path.unlink(missing_ok=True)
            self.held = False



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
    global _LOG_PATH
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval-minutes", type=float, default=10.0)
    parser.add_argument("--attempts", type=int, default=6)
    parser.add_argument("--forever", action="store_true",
                        help="keep re-checking every interval instead of exiting when clean")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    args = parser.parse_args()

    _LOG_PATH = args.log
    lock = Lock(args.lock)
    if not lock.acquire():
        return 0
    try:
        attempt = 0
        while True:
            attempt += 1
            limit = "inf" if args.forever else str(args.attempts)
            log(f"attempt {attempt}/{limit}")
            try:
                if one_pass():
                    if not args.forever:
                        log("pipeline clean and published; stopping")
                        return 0
                    # Resident watcher: keep the same beat while healthy so a
                    # recovered connection or a new upstream commit lands soon.
                    log("clean; watcher heartbeat")
                    time.sleep(args.interval_minutes * 60)
                    continue
            except Exception as error:  # retry loop must survive any failure
                log(f"error: {error}")
            if not args.forever and attempt >= args.attempts:
                log("gave up after all attempts")
                return 1
            log(f"sleeping {args.interval_minutes:g} min")
            time.sleep(args.interval_minutes * 60)
    finally:
        lock.release()


if __name__ == "__main__":
    sys.exit(main())
