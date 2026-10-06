# labxscut.github.io — LabX site

Public site of **LabX**, the AI-for-Science group at the School of Mathematics,
South China University of Technology. The group site uses the
[Greene Lab Website Template](https://github.com/greenelab/lab-website-template);
individual profile pages use an al-folio-inspired academic homepage structure
while sharing the lab template's styles and assets.

## Layout

| Path | Role |
|------|------|
| `index.md` | front door: research themes, tools, people, and news |
| `tools/` | collective tools index (per-tool docs stay in their own folders) |
| `people/` | collective roster and al-folio-inspired `/people/<nick>/` profiles |
| `publications/` | published and accepted papers, generated and deduplicated from the lab registry |
| `blog/`, `_posts/` | group notes and updates |
| `activities/` | seminars, workshops, and other group activities |
| `resources/` | lab identity, address, brand assets, citation notes |
| `research/`, `join/` | collective research themes and contact information |
| `deeplb/`, `sxLaep/` | tool-specific documentation folders (hand-maintained, update in place) |
| `_data/`, `_includes/`, `_layouts/`, `_plugins/`, `_styles/`, `images/` | data, Greene template components, and shared assets |

## Generated files (do not hand-edit)

* `_data/publications.yml` — from `~/work/advisee/hc/labxManage/Paper/*/publication.yaml`
  (published and accepted records; duplicates, WIP, under-review, and placeholders are excluded).
* `_data/people.yml` and `/people/<nick>/index.md` — from `~/work/advisee/core/database/contact.md`.
  Only public-safe fields are copied; emails, phone numbers, chat ids, leaders, and
  notes stay in the roster. Legacy `/<nick>/` URLs redirect to the nested profiles.

Member pages show only verified roster, software, and publication information;
they do not invent biographies or photos.

The publications index is based on the LabX paper registry and is not guaranteed
to include the PI's full Google Scholar bibliography. The tools catalog links
projects and papers where that relationship is recorded in the lab data.

## Regenerating

```bash
cd ~/work/labxscut/labxscut.github.io
python3 -m pip install -r requirements.txt
python3 _generators/gen_publications.py
python3 _generators/gen_people.py
```

Build a local preview after installing the Ruby dependencies with Bundler:

```bash
cd ~/work/labxscut/labxscut.github.io
bundle install
bundle exec jekyll build --destination /tmp/labxscut-site-preview
```

The generated preview is outside the repository; `/tmp/`, `_site/`, and Bundler
artifacts are ignored locally.

The public GitHub Pages configuration remains unchanged on its existing
`main:/` source; this local rebuild does not switch deployment modes or publish
changes. The repository is temporarily excluded from the hourly
`htworkrepos-sync` job while the rebuild stays local; remove its entry from
`~/work/agents/scripts/sync-work-repos.conf` when automatic sync should resume.

The template source is distributed under its BSD 3-Clause license in
[`LICENSE-LWT.md`](./LICENSE-LWT.md); its citation metadata is in
[`CITATION-LWT.cff`](./CITATION-LWT.cff).
