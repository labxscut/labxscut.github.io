# labxscut.github.io — LabX site

Public site of **LabX**, the AI-for-Science group at the School of Mathematics,
South China University of Technology. The group site uses the
[Greene Lab Website Template](https://github.com/greenelab/lab-website-template);
individual profile pages share its assets and visual system, with an academic
homepage layout.

## Layout

| Path | Role |
|------|------|
| `index.md` | front door: research themes, tools, people, and news |
| `tools/` | collective tools index (per-tool docs stay in their own folders) |
| `people/` | collective roster; each current member has a `/<nick>/` profile folder |
| `publications/` | published papers only, generated from the lab paper records |
| `resources/` | lab identity, address, brand assets, citation notes |
| `research/`, `join/` | collective research themes and contact information |
| `deeplb/`, `sxLaep/` | tool-specific documentation folders (hand-maintained, update in place) |
| `_data/`, `_includes/`, `_layouts/`, `_plugins/`, `_styles/`, `images/` | data, Greene template components, and shared assets |

## Generated files (do not hand-edit)

* `_data/publications.yml` — from `~/work/advisee/hc/labxManage/Paper/*/publication.yaml`
  (published records only; WIP / under-review / placeholder records are excluded).
* `_data/people.yml` and `/<nick>/index.md` — from `~/work/advisee/core/database/contact.md`.
  Only public-safe fields are copied; emails, phone numbers, chat ids, leaders, and
  notes stay in the roster.

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

GitHub Actions builds and deploys the site from `main`. In repository Settings,
set **Pages → Build and deployment → Source** to **GitHub Actions** before the
first deployment. The hourly `htworkrepos-sync` job also commits and pushes
changes made under `~/work`.

The template source is distributed under its BSD 3-Clause license in
[`LICENSE-LWT.md`](./LICENSE-LWT.md); its citation metadata is in
[`CITATION-LWT.cff`](./CITATION-LWT.cff).
