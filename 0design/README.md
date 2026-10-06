# LabX website design handoff

This folder contains internal owner decisions and implementation context for
future coding agents. It is not website content. Keep it excluded from the
generated site and do not publish private roster/contact information.

## Product and implementation

- This repository is the public LabX site for the AI-for-Science group at the
  School of Mathematics, South China University of Technology.
- The site is Jekyll, based on the Greene Lab Website Template; member profiles
  use an al-folio-inspired structure. Preserve the template's BSD 3-Clause
  attribution and license files.
- `index.md` is the public landing page. Shared presentation lives in
  `_includes/`, `_layouts/`, `_styles/`, and `_plugins/`; content/data live in
  the numbered sections and `_data/`.
- The top-level numbered folders are an intentional owner convention: their
  numeric prefixes represent the top-navigation order, not page titles.

## Navigation and numbered sections

| Folder | Navigation label | Order |
| --- | --- | ---: |
| `1news/` | News | 1 |
| `2about/` | Overview | 2 |
| `3team/` | Team | 3 |
| `4tools/` | Tools | 4 |
| `5publications/` | Publications | 5 |
| `6activities/` | Activities | 6 |
| `7engage/` | Opportunities / contact | 7 |

Keep each landing page's `nav.order` consistent with the folder prefix. These
prefixes are filesystem organization only: Jekyll derives URLs from paths, so
preserve intended public URLs with explicit permalinks and redirects. Audit
internal links, generated pages, and generator output whenever a numbered
folder is moved or renamed.

## Content and data rules

- `_data/people.yml` and member pages are generated from the lab roster by
  `_generators/gen_people.py`; `_data/publications.yml` is generated from the
  publication registry by `_generators/gen_publications.py`. Regenerate from
  their sources rather than editing generated output by hand.
- Publish only verified, public-safe roster fields. Never expose email,
  telephone, chat IDs, leader assignments, or private notes from the roster.
  Do not invent biographies, credentials, photos, or funding availability.
- The publication list includes records marked published/accepted after
  deduplication; it is not a claim of a complete Google Scholar bibliography.
- Link a project to a paper only when that relationship is recorded in the
  lab data. Keep tool documentation in its project-specific documentation
  rather than copying it into the collective catalog.
- Preserve existing public URLs where practical. If a URL must change, add and
  verify a redirect; do not assume a folder rename is URL-neutral.

## Profiles

The intended member URL pattern is `/team/<nick>/`, with CV, publications,
teaching (faculty only), and tools sections below that route. The generator writes physical
pages under `3team/` and sets explicit `/team/<nick>/...` permalinks. Legacy
`/people/` URLs redirect to their `/team/` counterparts.
Generated section pages use `member-section` and the section definitions in
`_data/profile_sections.yml`. Preserve the generator's overwrite protection
for hand-maintained pages. Treat the roster as the source of truth and show
only verified profile data.

## Build and deployment

- GitHub Pages is configured for the legacy `main` branch, repository root
  (`main:/`). Pushing a tag alone does not deploy; a successful Pages build on
  `main` is required.
- Build locally with `bundle exec jekyll build` after installing the Ruby
  dependencies (see the root README). The current Windows PowerShell session
  does not have `bundle` on `PATH`; use the configured Ruby/Bundler environment
  or WSL rather than assuming a local build succeeded.
- Verify the generated site and the GitHub Pages deployment run before
  describing a change as live.
- Do not stage all files, discard changes, or rewrite tags to make deployment
  easier. Inspect the working tree and publish only the intended site changes.

## Handoff status (2026-10-06)

- The owner has renamed/reorganized local section directories to the numbered
  names above. Those changes are currently local and uncommitted; the old
  tracked paths appear deleted and the new directories appear untracked.
  Preserve them and review the complete rename/link/generator diff before
  committing. Do not deploy only the older tracked tree by mistake.
- The local tree now has explicit permalinks for the seven section pages,
  `/team/<nick>/` permalinks for generated profiles, generated member
  section routes, and redirects for the moved `/deeplb/` and `/sxLaep/` docs.
  These changes still need a Pages build to validate.
- Tag `v2026.10.06` points to commit `ae84436`; do not move it. Pages builds
  exposed several Liquid/Jekyll incompatibilities. Commits `01cdcad` and
  `b98b127` were pushed to `main` to simplify a compound CSS `where_exp` and
  guard background URLs against rendered markup. The latest build at handoff
  still fails on a compound `where_exp` in the old `publications/index.md`.
  The numbered `5publications/index.md` has since been rewritten to use a
  Liquid loop, but that local change has not yet been pushed or validated by
  Pages.
- The tag exists remotely, but `gh release view v2026.10.06` reported that no
  GitHub Release object exists. Create or update a release only after agreeing
  which commit represents the deployable site; do not move the existing tag.
- At handoff, `main` is at `b98b127` and the numbered-directory work remains
  uncommitted. The working tree also contains site files outside those
  directories; inspect status before any commit.
