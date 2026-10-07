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
  the named sections and `_data/`.
- Public section folder names should match their canonical browser paths.
  Avoid numeric prefixes so filesystem paths and navigation links are easy
  to compare.

## Navigation and canonical paths

Keep this tab order and use the matching section folder and canonical URL:

| Order | Folder | Navigation label | Canonical URL |
| ---: | --- | --- | --- |
| 1 | `news/` | News | `/news/` |
| 2 | `about/` | About | `/about/` |
| 3 | `team/` | Team | `/team/` |
| 4 | `tools/` | Tools | `/tools/` |
| 5 | `publications/` | Publications | `/publications/` |
| 6 | `activities/` | Activities | `/activities/` |
| 7 | `engage/` | Engage | `/engage/` |

Each landing page's `nav.order` is the source for tab ordering and must match
this table. Keep folder names, canonical permalinks, and navigation links
aligned. Preserve changed historical URLs with redirects; `/blog/` redirects
to the canonical News path `/news/`. Audit internal links, generated pages,
and generator output whenever a section path changes.

## Visual identity and contact

- Use the LabX `images/logo.png` mark, not the SCUT seal.
- New visitors start in dark mode with a deep navy/blue palette. The selectable
  light theme uses warm brown and gray neutrals; keep both palettes readable.
- The public contact email is `lcxia@scut.edu.cn`.
- The PI's verified ORCID is `https://orcid.org/0000-0003-0868-1923`.
- Keep the footer free of the template credit and school/university attribution
  line. The contact address and other institutional context elsewhere are
  separate site information.

## Content and data rules

- `_data/people.yml` and member pages are generated from the lab roster by
  `_generators/gen_people.py`; `_data/publications.yml` is generated from the
  publication registry by `_generators/gen_publications.py`. Regenerate from
  their sources rather than editing generated output by hand.
- Curate verified public CV PDF links in `_data/member_profiles.yml`. When
  reviewing a member's GitHub material, check for the person's same-named
  public repository and confirm the PDF itself before adding its `cv_url` and
  `cv_repository_url`; never guess links or expose private material.
- Use [`labxscut.github.io.md`](./labxscut.github.io.md) as the readable,
  structured intake template for research directions, people, publications,
  tools, and courses. It is internal curation guidance, not live site data;
  promote verified and approved records into the canonical `_data/*.yml`
  sources.
- Publish only verified, public-safe roster fields. Never expose email,
  telephone, chat IDs, leader assignments, or private notes from the roster.
  Do not invent biographies, credentials, photos, or funding availability.
- The publication list includes records marked published/accepted after
  deduplication; it is not a claim of a complete Google Scholar bibliography.
- Google Scholar is the reference for the PI's full publication list. Current
  automated requests return incomplete pages; do not claim the registry is
  complete or add guessed records. Request an owner-provided BibTeX/CSV export
  if Scholar continues to block a complete comparison.
- Link a project to a paper only when that relationship is recorded in the
  lab data. Keep tool documentation in its project-specific documentation;
  do not duplicate paper details in the Tools catalog.
- Preserve existing public URLs where practical. If a URL must change, add and
  verify a redirect; do not assume a folder rename is URL-neutral.

## Tool documentation ownership and agent-triggered publishing

Each tool repository is the source of truth for its user-facing documentation.
The website contains a generated copy for GitHub Pages; agents must not hand-edit
that copy. Refreshing a tool page is an explicit agent action, not a push hook,
scheduled job, browser-time fetch, or Pages-build-time fetch.

### Repository contract

- Participating tool repositories maintain a predictable static payload at
  `docs/site/`, with `index.html` and all local stylesheets, scripts, images, and
  linked pages needed by the public docs.
- Keep relative assets and links inside that docs subtree. Avoid root-relative
  links such as `/assets/...`, which escape the tool's published prefix.
- If documentation needs generation, keep the generator and its verification
  in the tool repository. The site sync copies the static payload; it does not
  rebuild tool software or infer a tool-specific build.
- Tool owners review and merge the docs source on both `main` and `release`.
  Keep both branches available on `origin`; do not create or push a branch as a
  side effect of the website sync.
- Keep legacy project Pages redirects outside `docs/site/` (for example,
  sxLaep's redirect at `docs/index.html`) so a canonical page cannot overwrite
  its redirect.

### Explicit website refresh

- Use `_data/tools.yml` as the explicit catalog of tool repo, slug, source path,
  and immutable source refs. Never derive repository names or routes from a
  display name.
- Run `python scripts/sync_tool_docs.py --tool <deeplb|sxLaep|sxSNF>` only when
  an agent is explicitly asked to refresh that tool. The script fetches
  `origin/main` and `origin/release`, verifies both `docs/site/index.html`
  payloads and local links, and refuses to overwrite dirty site targets.
- The tool's `main` docs publish at `/tools/<docs_slug>/`; its `release` docs
  publish at `/tools/<docs_slug>/release/`. Preserve the existing capitalization
  for sxSNF (`/tools/sxSNF/`) and lowercase sxLaep (`/tools/sxlaep/`).
- The script records the immutable main and release commit IDs in that tool's
  `_data/tools.yml` entry and updates only the selected tool's page and metadata.
  It changes the local website worktree only: it does not commit or push any
  tool or website repository. Review the diff, validate the site, then publish
  the website through its configured Pages source on `main:/`.
- If either source branch or its docs output is absent/invalid, fail the sync.
  Do not silently skip the branch, publish stale files as success, or add broad
  credentials. Only public, approved documentation belongs in `docs/site/`.

### Auto-retry publishing

- `python scripts/auto_retry_sync.py --interval-minutes 10 --attempts 6` runs the
  whole publish path (sync all three tools, commit, push, verify `origin/main`)
  and repeats every 10 minutes only while a step fails, so transient GitHub
  `remote: Internal Server Error` push failures no longer need a manual re-run.
  It stops as soon as the pipeline is clean.
- `--forever` turns the same driver into a resident watcher: it keeps re-checking
  (every 10 minutes when something failed, every 30 minutes when clean), so a
  recovered network connection or a new upstream doc commit gets published without
  waiting for the hourly tick. It appends to `../logs/auto_retry_sync.log` and
  holds `../logs/auto_retry_sync.lock`; any second instance exits 0 immediately,
  which makes overlapping launches harmless.
- The watcher starts at logon from the user Startup folder
  (`labx-auto-retry-sync.bat`) and a host automation ("Tool docs auto-retry sync",
  hourly) launches the bounded driver as a backstop that takes over if the watcher
  died. The scheduler's finest granularity is hourly, so the 10-minute cadence
  lives in the script rather than in the schedule.

### Current integrated tools

sxLaep, sxSNF, and DeepLB each have the current public page payload under their
tool repo's `docs/site/` on `main` and `release`. The website's old sxLaep and
sxSNF Pages URLs redirect to their canonical tool routes; `/deeplb/` remains a
legacy route and should redirect to `/tools/deeplb/`. Verify all canonical and
legacy URLs after a website deployment.

## Profiles

The intended member URL pattern is `/team/<nick>/`. Only create/link a member
profile when there is verified CV, publication, faculty teaching, or tool
material. Only render tabs with material; do not use a generic placeholder CV.
Teaching is faculty-only and links directly to course material hosted by
GitHub/Gitee/Ulearning so each platform controls access. The generator writes
physical pages under `team/` and sets explicit `/team/<nick>/...` permalinks.
Legacy `/people/` URLs redirect to their `/team/` counterparts. Do not add a
Who tab or repeat selected tools/papers on the profile landing page.
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

## Handoff priorities

- When changing section names or paths, verify navigation order, canonical
  routes, redirects, and the deployed Pages build before describing the change
  as live.
- Check the repository-root `todo.md` for current deployment and content work.
- The full Google Scholar bibliography requires a complete owner-provided
  export. Never represent the current LabX registry as complete without that
  comparison.
