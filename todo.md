# LabX website handoff

## Priority

Keep the website building and deployed. Finish owner-requested site changes
before spending time on optional profile details.

## Changes in progress

- [x] Replace the SCUT seal with the local LabX logo in `images/logo.png`.
- [x] Default new visitors to the dark navy/blue palette; use warm brown/gray
  colors in light mode and make the header/footer follow the selected theme.
- [x] Rename the visible top-level sections to About and Engage, with redirects
  preserved from `/research/` and `/join/`.
- [x] Set the public contact email to `lcxia@scut.edu.cn` and remove the
  template/affiliation credit line from the footer.
- [x] Remove the Who tab and the profile landing-page copies of tool and paper
  lists. Do not repeat related paper details under the Tools catalog.
- [x] Generate individual Team links/pages only for current members with
  verified CV, publication, faculty teaching, or tool material. Render only
  profile sections that have material; Teaching is faculty-only.
- [x] Add PI ORCID `0000-0003-0868-1923`.
- [x] Add verified ISLDSu course links to the PI Teaching section. The GitHub
  repository requires authorization (the public fetch returned 404); the
  Ulearning destination is access-controlled by Ulearning. No verified Gitee
  mirror was found.
- [x] Fix live profile rendering so profile pages bypass the generic section
  parser, preventing duplicated/malformed profile markup; prefer the deployed
  LabX PNG over the missing SVG logo.
- [x] Move every section intro paragraph into one hand-editable data file,
  `_data/intros.json`, rendered by `_includes/intro.html` with `{pi}`,
  `{email}`, `{unit}`, `{university}`, `{scholar}`, `{published}`,
  `{accepted}`, and `{role}` placeholders. Empty strings hide an intro.

## Remaining blockers

- [x] Backfill publications and tool links into the pre-2022 records, and create
  registry entries for every Google Scholar item (including book chapters), so
  the site bibliography can approach the Scholar record. 41 records come from
  the CV (_generators/backfill_cv_papers.py) and 15 from the Google
  Scholar / ORCID / Crossref survey (_generators/backfill_scholar_papers.py);
  the labxManage registry now holds 116 paper folders. Scholar-only items stay
  out of the site bibliography via published_on_site: false, and the one
  published article that was missing (WangGMR2013ThelperDifferentiation) is
  now rendered. 	ool.papers in _data/tools.yml links each tool to its
  publication slugs (site and registry-only); qa_check.py reports the
  registry-only ones as pending promotion.
- [x] Section the publications into (co)-first/(co)-corresponding author work
  and collaborative work, following the `hc/0fund` CV format. Each record now
  carries `category`, `pi_role`, and `pi_track`; `/publications/` and the
  profile publications tab render three tracks (lead, collaborative, book
  chapters) with per-track intros in `_data/intros.json`.
- [x] Add a logo to each `labxscut/<tool>` repository, show it on
  `/tools/<tool>/`, and stamp each tool page with the source commit its data
  were collected from. `_generators/gen_tool_logos.py` draws the marks,
  `scripts/publish_tool_logos.py` opens the upstream PRs, `_data/tools.yml`
  holds `logo:`, and `_includes/tool-provenance.html` names the
  `docs_ref`/`docs_release_ref` commits recorded by `scripts/sync_tool_docs.py`.
- [x] Show the papers a tool was published in on `/tools/`: `tool.papers`
  slugs are rendered by `_includes/tool-papers.html` and cross-validated in
  both directions by `_generators/qa_check.py`.
- [ ] Complete the PI bibliography against Google Scholar. Automated requests
  are returning only partial citation data, so the current site registry is
  not a complete match. Ask the owner for a Google Scholar BibTeX/CSV export,
  then merge and deduplicate only verified published papers.

## Latest deployment

- Commit `9a0b042` is pushed to `main`; GitHub Pages build and deployment run
  [#34](https://github.com/labxscut/labxscut.github.io/actions/runs/37559440646)
  passed.
- Live checks passed for `/team/lcx/`, `/team/lcx/teaching/`, and `/about/`:
  one profile shell per member page, no malformed wrapper/artifact, PNG logo
  rendered, course links present, and ordinary content sections preserved.
- A local Jekyll build remains unavailable because Ruby/Bundler are not on
  the Windows PATH; the successful GitHub Pages build is the deployment
  authority.

## Constraints and verification

- Google Pages uses the repository root on `main` (`main:/`). A successful
  Pages deployment is required before describing a change as live.
- The live GitHub Pages runtime is Jekyll 3.10/Liquid 4.0/Sass 3.7. Avoid
  compound `where_exp` expressions and Sass `max()`/`min()` around `calc()`.
- The profile generator is `_generators/gen_people.py`; generated
  `_data/people.yml` and profile pages must be regenerated from source.
  Preserve its refusal to overwrite hand-maintained pages.
- Do not publish private roster details, student records, credentials, or
  course materials. Teaching links must leave authorization to the hosting
  service.
- Do not claim the Scholar bibliography is complete until compared against a
  full owner-provided export.
