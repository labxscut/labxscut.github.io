# Site deployment handoff

## Priority

Get the existing site building and deployed on GitHub Pages before adding or
polishing content. The owner wants a usable site first; do not spend time
filling out biographies or other optional details.

## Current state

- Repository: `D:\work\labxscut\labxscut.github.io`
- Branch: `main`
- The deployed site revision is `6c75a12` (`fix: emit section spacing max as
  CSS`).
- GitHub Pages uses the legacy `main:/` source. A push to `main` triggers the
  Pages build/deploy.
- Pages run [#30](https://github.com/labxscut/labxscut.github.io/actions/runs/37492378758)
  for commit `6c75a12` completed successfully, including both build and deploy.
- Public HTTP checks returned 200 for `/`, `/team/`, and `/team/lcx/`.
  `/people/` returns the expected redirect page pointing to `/team/`.
- A live-page check found one visual asset issue: Pages left the template's
  `file_read | google_fonts` filters unevaluated and emitted a broken
  `_styles/-theme.scss` font URL. A direct Google Fonts URL is now in
  `_includes/fonts.html`; this last polish fix is not yet deployed.
- Release `v2026.10.07` was created from deployed commit `6c75a12` and is
  published at
  https://github.com/labxscut/labxscut.github.io/releases/tag/v2026.10.07.
  The older `v2026.10.06` tag was not moved.
- The latest remote Pages run is `37484144252` (run 28), failed at
  `b98b127`. Its first failure was a Liquid syntax error in the old
  `publications/index.md`, caused by a `where_exp` condition. The replacement
  `5publications/index.md` uses Liquid loops. Run 29 then exposed the legacy
  Sass `max(calc(...))` incompatibility; commit `6c75a12` fixed it using
  `unquote`.
- No local Jekyll build was possible in the current Windows environment:
  `ruby` and `bundle` are not available on `PATH`; the remote Pages build is
  the authoritative validation.

## Work completed

- Reorganized the top sections into numbered folders `1news/` through
  `7engage/`; section index pages preserve their intended public routes.
- Renamed `3people/` to `3team/`, changed the visible title to Team, and moved
  profile routes to `/team/`. Added redirects from legacy `/people/` routes.
- Kept individual profiles and their CV, publications, and tools sections.
  Teaching is generated and shown only for faculty (including the PI); the
  generated Teaching pages were removed from the other 30 profiles. Six
  faculty profiles currently have Teaching pages.
- Updated navigation, internal links, profile generation, and README/design
  handoff documentation.
- Added `0design/README.md` and `AGENTS.md` for future-agent context; Jekyll
  excludes these internal notes from the published site.
- Fixed the earlier background-image Liquid/URI issue and simplified the
  stylesheet filter in commits already pushed to `main`.
- Local checks passed: Python syntax validation for `_generators/gen_people.py`,
  route/count checks for 36 profiles and 114 profile-section pages, and
  `git diff --check` (using `core.whitespace=cr-at-eol`).

## Immediate next steps

1. Commit and push the pending font-URL fix and this handoff update. Confirm the
   new Pages build and deploy succeed.
2. Recheck `/team/` for the direct font URL and verify the main routes again.
3. After that, avoid optional profile-content work until requested; the user
   prioritizes a running site over fully populated profiles.

## Known constraints

- GitHub Pages currently builds with `github-pages v232`, Jekyll `3.10.0`,
  Liquid `4.0.4`, and Sass `3.7.4`; the repository Gemfile's Jekyll 4
  dependency was not honored by that Pages build. Keep Liquid expressions
  compatible with the actual Pages runtime, avoid compound `where_exp`
  predicates, and avoid Sass `max()`/`min()` numeric functions with CSS
  `calc()` expressions.
- Pages is live and verified at the public URLs above. The deployment blockers
  from the earlier attempts (Liquid `where_exp` parsing and Sass 3.7 CSS
  `max(calc(...))` parsing) are fixed in the deployed revision.
- The font URL fix is pending validation and deployment.
- Keep the restraint on optional profile content.
