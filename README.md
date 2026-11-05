# labxscut.github.io — LabX site

Public site of **LabX**, the AI-for-Science group at the School of Mathematics,
South China University of Technology. The group site uses the
[Greene Lab Website Template](https://github.com/greenelab/lab-website-template);
individual profile pages use an al-folio-inspired academic homepage structure
while sharing the lab template's styles and assets.

## Agent guidance

Before changing site structure, navigation, member pages, or deployment, read
[`0design/README.md`](./0design/README.md). Keep the design handoff private
and out of the generated GitHub Pages site.

## Layout

| Path | Role |
|------|------|
| `index.md` | front door: research themes, tools, people, and news |
| `news/`, `_posts/` | group news, notes, and updates (`/news/`) |
| `about/` | About: research themes and group overview (`/about/`) |
| `team/` | collective roster and al-folio-inspired `/team/<nick>/` profiles |
| `tools/` | collective tools index and project documentation (`/tools/`) |
| `publications/` | published and accepted papers, generated and deduplicated from the lab registry (`/publications/`) |
| `activities/` | seminars, workshops, and other group activities (`/activities/`) |
| `engage/` | Engage: opportunities and contact information (`/engage/`) |
| `_data/`, `_includes/`, `_layouts/`, `_plugins/`, `_styles/`, `images/` | data, Greene template components, and shared assets |

Section intro prose lives in one hand-editable file, `_data/intros.json`, and is
rendered through `_includes/intro.html`. Every page section has a slot (empty
strings hide the intro); `{pi}`, `{email}`, `{unit}`, `{published}`, and the
other placeholders documented in the file's `_readme` are substituted at build
time.

The section folder name, canonical browser path, and navigation label should
stay aligned. The navigation order is recorded in `0design/README.md` and in
each section page's `nav.order`. The old News URL `/blog/` redirects to
`/news/`.

## Generated files (do not hand-edit)

* `_data/publications.yml` — from `~/work/advisee/hc/labxManage/Paper/*/publication.yaml`
  (published and accepted records; duplicates, WIP, under-review, and placeholders are excluded).
  The registry is kept close to the PI's full bibliography: `_generators/backfill_cv_papers.py`
  adds records found only in the CV, and `_generators/backfill_scholar_papers.py` adds records
  found only on Google Scholar / ORCID / Crossref (book chapters, theses, conference abstracts,
  preprints). Those extra records carry `visibility`, `published_on_site`, and `origin`, and stay
  out of the site bibliography while `published_on_site` is `noshow` or `false`;
  promote one by clearing that term (and giving it a published lifecycle status)
  once the item is formally published.
  The same `published_on_site` term is the display switch for tools, people, and
  activities. See **What is shown on the site** below. `visibility` only records
  where a bibliography gap came from; it does not hide or show a page.
  Every entry carries the CV track it belongs to: `category` (the registry's own
  label), `pi_role` (the PI authorship note), and `pi_track` — `lead` for
  (co)-first/(co)-corresponding author work, `collaborative`, or `book-chapter`.
  `_generators/gen_publications.py` treats the section headings of
  `~/work/advisee/hc/0fund/00lcx-cv/LiXia.cv.en.md` as authoritative and falls
  back to the recorded authorship role for registry-only records.
* `_data/people.yml` and `/team/<nick>/index.md` — from `~/work/advisee/core/database/contact.md`
  and curated public CV links in `_data/member_profiles.yml`. Only public-safe
  fields are copied; emails, phone numbers, chat ids, leaders, and notes stay
  in the roster. CV links must point to verified PDFs in public GitHub
  repositories named for the member. Legacy `/<nick>/` URLs redirect to the
  nested profiles.
* `images/avatars/<nick>.svg` — deterministic cartoon busts drawn by
  `_generators/gen_avatars.py` for members without a supplied photo.
* `images/tools/<tool>.svg` — tool marks drawn by `_generators/gen_tool_logos.py`;
  `scripts/publish_tool_logos.py` opens the matching pull request in each
  `labxscut/<tool>` repository, and `_data/tools.yml` records the accepted path
  in `logo:`.

`_data/tools.yml` is hand-maintained except for the provenance keys
(`docs_repo`, `docs_ref`, `docs_ref_date`, `docs_release_ref`,
`docs_release_ref_date`, `docs_path`, `docs_slug`) that
`scripts/sync_tool_docs.py` rewrites on every documentation sync;
`_includes/tool-provenance.html` renders them as the commit stamp on `/tools/`.
The papers a tool was published in live in `tool.papers` (publication slugs),
are rendered by `_includes/tool-papers.html`, and are cross-validated in both
directions by `_generators/qa_check.py`.

Member pages are generated only when a current member has verified CV,
publication, faculty teaching, or tool material. They do not invent
biographies or photos. Teaching tabs are shown only for faculty.

The publications index is based on the LabX paper registry and is not guaranteed
to include the PI's full Google Scholar bibliography. The tools catalog lists a
tool's papers as links into `/publications/` only; the bibliographic details
live in the publication records.

## What is shown on the site

`published_on_site` marks a **tool**, **person**, **publication**, or **activity**
as displayed or not. Leave the key out, or set it to `true`, and the entry is
shown. Set it to `noshow` and the entry stays in the repository but drops out of
listings, index cards, cross-links, navigation chips, generated click order,
and the sitemap on the next site build. `false` means the same thing; older
publication records already use it. No generator has to run before a `noshow`
value already stored in `_data` takes effect. The source is not deleted.

This is not the tool `private: true` flag. A private tool is still listed; only
its unreachable repository URL is withheld. It is also not publication
`visibility`, which classifies a bibliography gap as `registry` or `scholar-only`.
News stays on its own switch: rename the file with a leading `_` (`_news/README.md`).

GitHub Pages builds this site in safe mode and does not load `_plugins`, so the
switch is data plus Liquid plus Jekyll's own publish controls. Every listing
keeps an entry unless `published_on_site` is `noshow` or `false`. A direct URL
for a noshow entry is not built, so it 404s.

| Kind | Where the flag is set | What remains in the repo | What a visitor gets |
| --- | --- | --- | --- |
| Tool | `_data/tools.yml` | The catalog entry and, when the tool has hosted docs, `tools/<docs_slug>/` | No card on `/` or `/tools/`, and no link from a paper, news chip, or member tools tab. Add `tools/<docs_slug>` to `_config.yml` `exclude` so `/tools/<docs_slug>/` (and its `release/` copy) is not emitted and is absent from `sitemap.xml`. |
| Person | `_data/member_profiles.yml`, as `nick` plus `published_on_site: noshow` | The roster row, copied onto `_data/people.yml` by `gen_people.py` | No row on `/team/` and no profile link. The generator writes `published: false` on `team/<nick>/`, so those pages 404 and stay out of the sitemap. A `noshow` already present on the people row is omitted from `/team/` on the next build. |
| Publication | `published_on_site: noshow` (or `false`) on the labxManage `publication.yaml` | The registry record | `gen_publications.py` omits a full paper from `_data/publications.yml`, so it has no listing and no anchor. There is no per-paper HTML page. Meeting abstracts and posters that have a DOI still render; that existing exemption is unchanged. A record that already carries `noshow` or `false` in site data is dropped by the publications template on this build. |
| Activity | `_data/activities.yml` | The activity entry | Omitted from `/` and `/activities/`. An activity has no page of its own. |

`_generators/qa_check.py` fails if a noshow tool with a `docs_slug` is
missing from `exclude`, or if a displayed tool's docs directory is excluded.
It also fails if a noshow person still has `has_page: true` or a profile
page without `published: false`.

**sxSIGMA** is `noshow`: `_data/tools.yml` sets `published_on_site: noshow`,
and `_config.yml` excludes `tools/sxsigma`. Both are already in the tree, so
the next Pages build drops the card and the docs URL with no generator step.
The documentation tree stays in the repository. Delete the term and the exclude
entry to show it again. `images/tools/sxSIGMA.svg` is still copied with the
other static images; no page links to it.

## Regenerating

```bash
cd ~/work/labxscut/labxscut.github.io
python3 -m pip install -r requirements.txt
python3 _generators/gen_publications.py
python3 _generators/gen_people.py
python3 _generators/gen_avatars.py
python3 _generators/qa_check.py
```

`_generators/qa_check.py` fails on dangling tool/paper cross-links, missing
years, and author names that resolve to neither the roster nor an affiliation.

Build a local preview after installing the Ruby dependencies with Bundler:

```bash
cd ~/work/labxscut/labxscut.github.io
bundle install
bundle exec jekyll build --destination /tmp/labxscut-site-preview
```

The generated preview is outside the repository; `/tmp/`, `_site/`, and Bundler
artifacts are ignored locally.

The public GitHub Pages source is the repository root on `main` (`main:/`).
Pushing to `main` triggers the Pages build and deployment; a tag alone does not
deploy. The repository is temporarily excluded from the hourly
`htworkrepos-sync` job; remove its entry from
`~/work/agents/scripts/sync-work-repos.conf` when automatic sync should resume.

The template source is distributed under its BSD 3-Clause license in
[`LICENSE-LWT.md`](./LICENSE-LWT.md); its citation metadata is in
[`CITATION-LWT.cff`](./CITATION-LWT.cff).
