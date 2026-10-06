# Site deployment handoff

## Priority

Get the existing site building and deployed on GitHub Pages before adding or
polishing content. The owner wants a usable site first; do not spend time
filling out biographies or other optional details.

## Current state

- Repository: `D:\work\labxscut\labxscut.github.io`
- Branch: `main`
- `main` and `origin/main` are at `5d1571c` (`docs: add deployment handoff
  checklist`); the working tree is clean.
- GitHub Pages uses the legacy `main:/` source. A push to `main` triggers the
  Pages build/deploy.
- Pages run [#29](https://github.com/labxscut/labxscut.github.io/actions/runs/37490903077)
  for commit `5d1571c` failed. It includes site changes from `6bf7e61` and
  this private handoff file.
- The new failure is in `_styles/section.scss:5`: the Pages runtime uses
  Sass 3.7, which interprets CSS `max()` as its Sass numeric function and
  rejects the `calc()` argument. A local compatibility fix now emits `max()`
  as CSS with Sass `unquote`; it has not yet been pushed or tested remotely.
- The latest remote Pages run is `37484144252` (run 28), failed at
  `b98b127`. Its first failure was a Liquid syntax error in the old
  `publications/index.md`, caused by a `where_exp` condition. The replacement
  `5publications/index.md` uses Liquid loops and is included in local commit
  `6bf7e61`.
- No local Jekyll build was possible in the current Windows environment:
  `ruby` and `bundle` are not available on `PATH`.
- No successful build or deployment of commit `6bf7e61` has been confirmed.

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

1. Commit and push the pending `_styles/section.scss` compatibility fix and
   this updated handoff, then inspect the resulting Pages run. If it fails,
   fix the first actual error only and repeat until build and deploy both
   succeed.
2. After a successful deployment, verify `https://labxscut.github.io/`,
   `/team/`, `/publications/`, and `/tools/`, and check that `/people/`
   redirects to `/team/`.
3. Only after deployment is healthy, resume the outstanding release request.
   Tag `v2026.10.06` already exists at `ae844361`; do not move it. The GitHub
   Release object was not present at the last check, so use a new, agreed
   release tag if publishing a release is still desired.

## Known constraints

- GitHub Pages currently builds with `github-pages v232`, Jekyll `3.10.0`,
  Liquid `4.0.4`, and Sass `3.7.4`; the repository Gemfile's Jekyll 4
  dependency was not honored by that Pages build. Keep Liquid expressions
  compatible with the actual Pages runtime, avoid compound `where_exp`
  predicates, and avoid Sass `max()`/`min()` numeric functions with CSS
  `calc()` expressions.
- Do not claim the site is live until the Pages build and deploy both succeed
  and the public URL is checked.
- Do not add optional profile content before the deployment blocker is cleared.
