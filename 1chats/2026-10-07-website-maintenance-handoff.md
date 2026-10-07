---
title: Redacted website-maintenance handoff
description: "Sanitized decisions and implementation status for future LabX website maintenance."
---

# Redacted website-maintenance handoff

This is a **sanitized summary**, not a raw chat export. Personal contact details,
individual member identifiers, credentials, private review/applicant material,
and unrelated personal information are intentionally omitted. The site repository
is public; do not add raw conversations here.

## Durable website decisions

- Keep the public site focused on getting the website usable before filling every
  profile or content detail. Use `0design/README.md` as the design/navigation
  source of truth and keep canonical paths consistent with visible links.
- Landing-page section order: introductory/About content, **Latest news**,
  Research, tools, activities, and news. Latest news is sourced from
  `_data/news.yml`.
- Keep the requested research organization to three themes: AI theory; AI for
  biomedical sciences; and AI for materials science and other emerging fields.
  Select papers should have short, evidence-based narratives. Structured source
  metadata belongs in `0design/labxscut.github.io.md`.
- Preserve the requested member-page layout: a fixed left profile panel occupying
  about one quarter of the view, with section content on the right; CV remains
  available from the profile. Populate personal and course details only from
  approved source repositories.
- Faculty-only teaching is needed. Course materials may link to Gitee, GitHub, or
  the learning platform; each source controls its own access.
- Avoid duplicate rendered content, stale navigation labels, unnecessary member
  links, and template marker text showing on pages. Keep tool documentation
  routes canonical and case-consistent.

## Documentation route migration

- Canonical sxLaep documentation: `/tools/sxlaep/`; the old `/sxLaep/` project
  URL redirects to it.
- Canonical sxSNF documentation: `/tools/sxSNF/`; the old `/sxSNF/` project URL
  redirects to it.
- Both canonical docs are checked-in snapshots pinned in `_data/tools.yml`.
  `0design/README.md` records the snapshot and the future build-time synchronization
  design. Do not replace snapshots with a live fetch or a success-shaped fallback:
  first establish a tracked, tested site deployment workflow, verify source refs,
  fail clearly if sync/build fails, and inspect the integrated output.
- A redirect generated into a docs index can be overwritten by the source
  documentation generator. The sxLaep redirect was made durable by updating both
  the committed index and its generator. Verify the generated redirect and the
  live legacy URL after future generator or Pages changes.

## Deployment and verification guardrails

- The website is a Jekyll user site; this differs from the separate tool repos'
  project Pages sites, which use static HTML under `docs/`.
- `0design/README.md` records the website's `main:/` Pages deployment. The local
  `.github/workflows/pages.yml` is ignored/untracked and is not authoritative.
  Before changing or reporting deployment behavior, inspect the tracked remote
  workflow and GitHub Pages source setting.
- Reconcile any deploy checks against current canonical routes before relying on
  them; an ignored workflow may contain stale route assertions.
- Build locally, check generated routes and redirects, then verify the successful
  published deployment and live URLs. A local build or commit alone does not
  establish that Pages is current.

## Current handoff state (2026-10-07)

- The live sxLaep and sxSNF canonical tool pages and both legacy redirects were
  checked; sxLaep's redirect is maintained by its docs generator.
- The landing-page **Latest news** section has just been moved to the second
  section in `index.md`. That edit is local and uncommitted/unpublished at the
  time of this note.
- Check `todo.md`, `0design/README.md`, current worktree status, and the actual
  Pages source before proceeding. Do not assume this handoff's historical state
  is still current.
