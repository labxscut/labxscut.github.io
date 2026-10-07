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
| `1news/`, `_posts/` | group news, notes, and updates |
| `2about/` | About: research themes and group overview (`/about/`) |
| `3team/` | collective roster and al-folio-inspired `/team/<nick>/` profiles |
| `4tools/` | collective tools index and project documentation |
| `5publications/` | published and accepted papers, generated and deduplicated from the lab registry |
| `6activities/` | seminars, workshops, and other group activities |
| `7engage/` | Engage: opportunities and contact information (`/engage/`) |
| `_data/`, `_includes/`, `_layouts/`, `_plugins/`, `_styles/`, `images/` | data, Greene template components, and shared assets |

The numeric prefixes on the section folders express the intended top-navigation
order. Explicit permalinks preserve established public URLs when the physical
folders use those prefixes.

## Generated files (do not hand-edit)

* `_data/publications.yml` — from `~/work/advisee/hc/labxManage/Paper/*/publication.yaml`
  (published and accepted records; duplicates, WIP, under-review, and placeholders are excluded).
* `_data/people.yml` and `/team/<nick>/index.md` — from `~/work/advisee/core/database/contact.md`.
  Only public-safe fields are copied; emails, phone numbers, chat ids, leaders, and
  notes stay in the roster. Legacy `/<nick>/` URLs redirect to the nested profiles.

Member pages are generated only when a current member has verified CV,
publication, faculty teaching, or tool material. They do not invent
biographies or photos. Teaching tabs are shown only for faculty.

The publications index is based on the LabX paper registry and is not guaranteed
to include the PI's full Google Scholar bibliography. The tools catalog does
not repeat publication details; paper/tool cross-links are maintained in the
publication records.

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

The public GitHub Pages source is the repository root on `main` (`main:/`).
Pushing to `main` triggers the Pages build and deployment; a tag alone does not
deploy. The repository is temporarily excluded from the hourly
`htworkrepos-sync` job; remove its entry from
`~/work/agents/scripts/sync-work-repos.conf` when automatic sync should resume.

The template source is distributed under its BSD 3-Clause license in
[`LICENSE-LWT.md`](./LICENSE-LWT.md); its citation metadata is in
[`CITATION-LWT.cff`](./CITATION-LWT.cff).
