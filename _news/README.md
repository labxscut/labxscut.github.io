# `_news/` — human-editable news front end

One announcement per markdown file. This is the durable, human-editable home for
news that is **not** a registry paper: tool releases, talks, awards, milestones,
and any announcement you want on `/news/` without touching the generated YAML.

`_data/news.yml` is **generated** — do not hand-edit it. Add a file here, then
run the generator:

```
python _generators/gen_news.py --write
```

## File format

`<stem>.md`, where `<stem>` becomes the entry's `source: news/<stem>`. Use a
date-prefixed stem so files sort chronologically, e.g. `20260518-sxlaep-release.md`.

```markdown
---
date: 2026-05-18          # required; any precision (YYYY, YYYY-MM, YYYY-MM-DD)
text: sxLaep v1.0.5 released.   # required; the one-line card headline
url: https://…           # optional; links the headline (DOI, docs page, …)
image: /images/news/foo.png     # optional; attachment thumbnail
alt: Optional alt text          # optional; defaults to `text`
attachments:                     # optional; downloadable links on the card
  - label: Poster
    url: /files/poster.pdf
---

Free prose here is for humans reading the file. Only the front matter is used.
```

### Rules

- **`text` is plain text.** The card and the home "Latest news" list render it
  literally, so markdown link syntax (`[x](y)`) would show up as raw brackets.
  Put the link in `url` instead.
- **Dates** follow the site convention: any precision is canonicalised to
  `YYYYMMDDHHMMSS` for sorting and shown as `YYYYMMDD`. A year-only date sorts
  at the start of that year and displays the bare year — never fabricate a
  month/day.
- **`image`** must point at a file in the repo (put it under `images/news/`).
  The generator warns if the path does not exist, so a typo shows up in the loop
  rather than as a broken image on the site.
- One item = one file = one clean diff. Deleting the file removes the entry on
  the next run.

## How the three feed writers coexist

`_data/news.yml` mixes three kinds of entry, each owned by exactly one writer, so
running them in any order is idempotent and never duplicates a paper:

| `source` | owned by | notes |
|---|---|---|
| `labxManage/Paper/<slug>` | `agents/skills/labx-manage-sync/labxmanage_news_aggregate.py` (labx_admin) | registry papers with broadcast evidence |
| `news/<stem>` | `_generators/gen_news.py` (this folder) | human announcements |
| *(none)* | legacy inline | preserved by both, but add new items here instead |

A `news/` entry whose `url` matches a managed paper **yields** to the managed
entry (the aggregator owns registry papers); a legacy inline row whose `url`
matches a `news/` entry is dropped, which is how the old hand-written rows were
migrated into this folder.
