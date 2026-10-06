# labxscut.github.io — LabX site

Public site of **LabX**, the AI-for-Science group at the School of Mathematics,
South China University of Technology. Served by GitHub Pages from `main` (Jekyll,
no plugins, no build step in CI).

## Layout

| Path | Role |
|------|------|
| `index.html` | front door: research themes, tools, people, news, contact |
| `tools/` | collective tools index (per-tool docs stay in their own folders) |
| `people/` | collective roster; each current member also has `/<nick>/` |
| `publications/` | published papers only, generated from the lab paper records |
| `resources/` | lab identity, address, brand assets, citation notes |
| `deeplb/`, `sxLaep/` | tool-specific documentation folders (hand-maintained, update in place) |
| `_people/`, `_data/`, `_includes/`, `_layouts/`, `assets/` | Jekyll data, templates, and styles |

## Generated files (do not hand-edit)

* `_data/publications.yml` — from `~/work/advisee/hc/labxManage/Paper/*/publication.yaml`
  (published records only; WIP / under-review / placeholder records are excluded).
* `_data/people.yml` and `_people/<nick>.md` — from `~/work/advisee/core/database/contact.md`.
  Only public-safe fields are copied (name, degree, years, GitHub handle, links);
  emails, phone numbers, chat ids, leaders, and notes stay in the roster.

## Regenerating

```bash
cd ~/work/labxscut/labxscut.github.io/_generators
python3 gen_publications.py && python3 gen_people.py
```

Local preview without a Jekyll install (uses the system `liquid` gem); output
defaults to `/tmp/labxscut-site-preview`:

```bash
cd ~/work/labxscut/labxscut.github.io
ruby _generators/preview.rb
python3 _generators/preview_check.py
```

Set `LABX_PREVIEW_DIR` to override the preview output directory.

GitHub Pages rebuilds the real site on every push to `main`; the hourly
`htworkrepos-sync` job also commits and pushes changes made under `~/work`.
