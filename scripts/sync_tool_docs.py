#!/usr/bin/env python3
"""Manually refresh LabX tool pages from their public repository docs/site trees."""

from __future__ import annotations

import argparse
import html.parser
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

SITE_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = SITE_ROOT / "tools"
TOOLS_DATA = SITE_ROOT / "_data" / "tools.yml"
SOURCE_ROOT = SITE_ROOT.parent
BRANCHES = ("main", "release")


@dataclass(frozen=True)
class Tool:
    key: str
    repository: str
    directory: str
    slug: str


TOOLS = {
    "deeplb": Tool("deeplb", "labxscut/DeepLB", "DeepLB", "deeplb"),
    "sxLaep": Tool("sxLaep", "labxscut/sxLaep", "sxLaep", "sxlaep"),
    "sxSNF": Tool("sxSNF", "labxscut/sxSNF", "sxSNF", "sxSNF"),
}
LEGACY_ROUTES = {
    "deeplb": ("/deeplb/",),
    "sxLaep": ("/sxLaep/",),
    "sxSNF": ("/sxSNF/",),
}
SOURCE_PATH = PurePosixPath("docs/site")
METADATA_KEYS = ("docs_repo", "docs_ref", "docs_release_ref", "docs_path", "docs_slug")
FORBIDDEN_PARTS = {".git", "private", "raw"}
FORBIDDEN_NAMES = {".env", "credentials", "secrets"}


class SyncError(RuntimeError):
    """Raised when a source or destination cannot be safely synchronized."""


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check and result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise SyncError(f"git {' '.join(args)} failed in {repo}: {detail}")
    return result


def git_blob(repo: Path, object_id: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "blob", object_id],
        check=False,
        capture_output=True,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise SyncError(f"Unable to read tool documentation blob {object_id}: {detail}")
    return result.stdout


def repository_path(tool: Tool) -> Path:
    repo = SOURCE_ROOT / tool.directory
    if not (repo / ".git").exists():
        raise SyncError(f"Tool repository is missing: {repo}")
    remote = git(repo, "remote", "get-url", "origin").stdout.strip().rstrip("/")
    normalized = remote.removesuffix(".git").casefold()
    # Accept both HTTPS (.../org/repo) and SSH (git@host:org/repo) origins.
    expected_suffixes = (
        f"/{tool.repository}".casefold(),
        f":{tool.repository}".casefold(),
    )
    if not normalized.endswith(expected_suffixes):
        raise SyncError(f"Unexpected origin for {repo}: {remote}")
    return repo


def fetch_refs(repo: Path) -> dict[str, str]:
    refspecs = [
        f"+refs/heads/{branch}:refs/remotes/origin/{branch}" for branch in BRANCHES
    ]
    git(repo, "fetch", "--no-tags", "origin", *refspecs)
    refs = {}
    for branch in BRANCHES:
        ref = f"refs/remotes/origin/{branch}"
        refs[branch] = git(repo, "rev-parse", "--verify", ref).stdout.strip()
    return refs


def validate_source_path(path: PurePosixPath) -> None:
    if path.is_absolute() or ".." in path.parts:
        raise SyncError(f"Unsafe path in tool docs: {path}")
    if not path.parts or path.parts[0] != SOURCE_PATH.parts[0]:
        raise SyncError(f"Tool docs are outside {SOURCE_PATH}: {path}")
    if any(part.casefold() in FORBIDDEN_PARTS for part in path.parts):
        raise SyncError(f"Private or repository metadata path is not publishable: {path}")
    name = path.name.casefold()
    if name in FORBIDDEN_NAMES or name.endswith((".pem", ".key")):
        raise SyncError(f"Potential credential file is not publishable: {path}")


def export_docs(repo: Path, ref: str, destination: Path) -> int:
    listing = git(repo, "ls-tree", "-r", "-z", ref, "--", f"{SOURCE_PATH}/")
    files = 0
    for record in listing.stdout.split("\0"):
        if not record:
            continue
        header, raw_path = record.split("\t", 1)
        mode, object_type, object_id = header.split()
        relative = PurePosixPath(raw_path).relative_to(SOURCE_PATH)
        validate_source_path(PurePosixPath(*SOURCE_PATH.parts, *relative.parts))
        if object_type != "blob" or mode not in {"100644", "100755"}:
            raise SyncError(f"Unsupported file type in {ref}: {raw_path}")
        if not relative.parts:
            raise SyncError(f"Unexpected empty documentation path in {ref}")

        output = destination.joinpath(*relative.parts)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(git_blob(repo, object_id))
        files += 1

    if files == 0 or not (destination / "index.html").is_file():
        raise SyncError(f"{ref}:{SOURCE_PATH} must contain a non-empty index.html")
    return files


class LinkCollector(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.links.append(value)


def validate_local_links(root: Path, slug: str) -> None:
    for page in root.rglob("*.html"):
        parser = LinkCollector()
        parser.feed(page.read_text(encoding="utf-8"))
        for value in parser.links:
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or value.startswith("//") or not parsed.path:
                continue
            if parsed.path.startswith("/"):
                prefix = f"/tools/{slug}/"
                if not parsed.path.startswith(prefix):
                    raise SyncError(f"Root-relative link escapes /tools/{slug}/: {value}")
                parts = PurePosixPath(unquote(parsed.path[len(prefix):]))
                if ".." in parts.parts:
                    raise SyncError(f"Root-relative link escapes its tool route: {value}")
                target = root.joinpath(*parts.parts)
            else:
                target = (page.parent / unquote(parsed.path)).resolve()
                if not target.is_relative_to(root.resolve()):
                    raise SyncError(f"Relative link escapes the published docs tree: {value}")
            if target.is_dir() or parsed.path.endswith("/"):
                target = target / "index.html"
            if not target.is_file():
                raise SyncError(f"Broken local link in {page.relative_to(root)}: {value}")


def update_tool_metadata(text: str, tool: Tool, refs: dict[str, str]) -> str:
    starts = list(re.finditer(r"(?m)^- key: ([^\r\n]+)\r?$", text))
    matches = [
        match
        for index, match in enumerate(starts)
        if match.group(1) == tool.key
    ]
    if len(matches) != 1:
        raise SyncError(f"Expected exactly one _data/tools.yml entry for {tool.key}")

    start = matches[0].start()
    next_start = next(
        (match.start() for match in starts if match.start() > start),
        len(text),
    )
    block = text[start:next_start]
    lines = block.splitlines()
    metadata = {
        "docs": f"https://labxscut.github.io/tools/{tool.slug}/",
        "docs_repo": tool.repository,
        "docs_ref": refs["main"],
        "docs_release_ref": refs["release"],
        "docs_path": str(SOURCE_PATH),
        "docs_slug": tool.slug,
    }
    filtered = [
        line
        for line in lines
        if not any(re.match(rf"^  {re.escape(key)}:", line) for key in metadata)
    ]
    docs_line = next(
        (index for index, line in enumerate(filtered) if line.startswith("  docs:")),
        None,
    )
    if docs_line is None:
        raise SyncError(f"Missing docs URL field in _data/tools.yml entry {tool.key}")
    for offset, (key, value) in enumerate(metadata.items(), start=1):
        filtered.insert(docs_line + offset, f"  {key}: {value}")
    replacement = "\n".join(filtered)
    if block.endswith("\n"):
        replacement += "\n"
    return text[:start] + replacement + text[next_start:]


def add_jekyll_front_matter(index: Path, permalink: str, legacy_routes: tuple[str, ...] = ()) -> None:
    body = index.read_text(encoding="utf-8")
    if body.startswith("---\n") or body.startswith("---\r\n"):
        raise SyncError(f"Source docs index must be plain HTML without Jekyll front matter: {index}")
    lines = ["---", "layout: null", f"permalink: {permalink}"]
    if legacy_routes:
        lines.append("redirect_from:")
        lines.extend(f"  - {route}" for route in legacy_routes)
    lines.extend(["---", ""])
    index.write_text("\n".join(lines) + body, encoding="utf-8", newline="")


def write_metadata(path: Path, text: str) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
        os.replace(temp_name, path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def ensure_clean_targets(tool: Tool) -> None:
    result = git(
        SITE_ROOT,
        "status",
        "--porcelain",
        "--untracked-files=all",
        "--",
        f"tools/{tool.slug}",
        "_data/tools.yml",
    )
    if result.stdout.strip():
        raise SyncError(
            "Refusing to overwrite local changes in the tool page or catalog:\n"
            + result.stdout.rstrip()
        )


def sync_tool(tool: Tool) -> None:
    repo = repository_path(tool)
    refs = fetch_refs(repo)
    ensure_clean_targets(tool)

    with tempfile.TemporaryDirectory(prefix=f"sync-{tool.key}-", dir=SITE_ROOT) as temp:
        staging = Path(temp)
        main_docs = staging / "main"
        release_docs = staging / "release"
        main_count = export_docs(repo, refs["main"], main_docs)
        release_count = export_docs(repo, refs["release"], release_docs)
        add_jekyll_front_matter(
            main_docs / "index.html",
            f"/tools/{tool.slug}/",
            LEGACY_ROUTES[tool.key],
        )
        add_jekyll_front_matter(
            release_docs / "index.html",
            f"/tools/{tool.slug}/release/",
        )
        staged_site = staging / tool.slug
        shutil.copytree(main_docs, staged_site)
        shutil.copytree(release_docs, staged_site / "release")
        validate_local_links(staged_site, tool.slug)

        catalog = TOOLS_DATA.read_text(encoding="utf-8")
        updated_catalog = update_tool_metadata(catalog, tool, refs)
        old_site = TOOLS_ROOT / tool.slug
        backup = staging / "previous"
        if old_site.exists():
            os.replace(old_site, backup)
        try:
            os.replace(staged_site, old_site)
            write_metadata(TOOLS_DATA, updated_catalog)
        except Exception:
            if old_site.exists():
                shutil.rmtree(old_site)
            if backup.exists() and not old_site.exists():
                os.replace(backup, old_site)
            raise

        if backup.exists():
            shutil.rmtree(backup)

    print(
        f"{tool.repository}: main {refs['main'][:12]} ({main_count} files) -> "
        f"/tools/{tool.slug}/; release {refs['release'][:12]} "
        f"({release_count} files) -> /tools/{tool.slug}/release/"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Agent-triggered refresh of one LabX tool page from that tool "
            "repository's origin/main and origin/release docs/site trees."
        )
    )
    parser.add_argument(
        "--tool",
        required=True,
        choices=sorted(TOOLS),
        help="Tool to refresh; both main and release are synchronized.",
    )
    args = parser.parse_args()
    try:
        sync_tool(TOOLS[args.tool])
    except (OSError, SyncError, subprocess.SubprocessError) as error:
        print(f"Tool documentation sync failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
