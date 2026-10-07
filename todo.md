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

## Remaining blockers

- [ ] Complete the PI bibliography against Google Scholar. Automated requests
  are returning only partial citation data, so the current site registry is
  not a complete match. Ask the owner for a Google Scholar BibTeX/CSV export,
  then merge and deduplicate only verified published papers.
- [ ] Commit and push the verified site changes to `main`; inspect the GitHub
  Pages build/deploy and verify the live navigation, logo, profile routes, and
  theme toggle. A local Jekyll build is unavailable because Ruby/Bundler are
  not on the Windows PATH.

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
