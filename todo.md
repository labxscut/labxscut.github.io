# Site deployment handoff

## Priority

Get the existing site building and deployed on GitHub Pages before adding or
polishing content. The owner wants a usable site first; do not spend time
filling out biographies or other optional details.

## Current state

- Repository: `D:\work\labxscut\labxscut.github.io`
- Branch: `main`
- The deployed site revision is `043cebe` (`fix: use a Pages-compatible font
  stylesheet`).
- GitHub Pages uses the legacy `main:/` source. A push to `main` triggers the
  Pages build/deploy.
- Pages run [#31](https://github.com/labxscut/labxscut.github.io/actions/runs/37494805517)
  for commit `043cebe` completed successfully, including both build and deploy.
- Public HTTP checks returned 200 for `/`, `/team/`, and `/team/lcx/`.
  `/people/` returns the expected redirect page pointing to `/team/`.
  `_styles/section.css` also returns 200. The Team page now has a direct Google
  Fonts stylesheet URL and no stale `_styles/-theme.scss` URL.
- Release `v2026.10.07` was created from deployed commit `6c75a12` and is
  published at
  https://github.com/labxscut/labxscut.github.io/releases/tag/v2026.10.07.
  The older `v2026.10.06` tag was not moved. The small font-loader correction
  in `043cebe` was deployed afterward.
- The latest remote Pages run is `37484144252` (run 28), failed at
  `b98b127`. Its first failure was a Liquid syntax error in the old
  `publications/index.md`, caused by a `where_exp` condition. The replacement
  `5publications/index.md` uses Liquid loops. Run 29 then exposed the legacy
  Sass `max(calc(...))` incompatibility; commit `6c75a12` fixed it using
  `unquote`. The direct font URL fix is in `043cebe`.
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

1. No deployment blocker remains. For any future code change, inspect the
   resulting Pages run and verify the public URL before describing that version
   as live.
2. Avoid optional profile-content work until requested; the user prioritizes a
   running site over fully populated profiles.

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
- The font URL fix is deployed and verified.
- Keep the restraint on optional profile content.
