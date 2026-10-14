---
date: YYYY-MM-DD
text: One-sentence award announcement, e.g. "LabX's marine enzyme preparation
  project received the 2026 Natural Resources Science and Technology Award."
url: https://…            # optional: the official 公示/announcement page
image: /images/news/award-example.png   # optional: certificate/notice thumbnail
alt: Award notice
attachments:                           # optional: downloadable files
  - label: Public notice
    url: /files/award-notice.pdf
---

TEMPLATE — not published. gen_news.py skips files whose name starts with `_`,
`.` or `README.md`, so this stays local documentation.

To publish an award:

1. PI ruling first — which awards are publishable. The award packs under
   advisee/trust/0award are PII-dense (完成人信息表 carries personal info,
   scans, contact details); NEVER point the site at that tree or copy those
   files. Only the fact of the award + any officially public notice text may
   appear.
2. Copy this file to a real name, e.g. `20261010-ziyr-award.md` (date-prefixed
   stem becomes `source: news/20261010-ziyr-award`).
3. Fill the front matter. `text` is plain text (no markdown links — put the
   link in `url`). Dates: any precision; the site shows YYYYMMDD.
4. If an image/attachment is used, place the FILE under images/news/ (or
   files/) and make sure it is public-safe (no personal info, no signatures,
   no ID numbers).
5. `python _generators/gen_news.py --write`, then `qa_check.py --links`, commit,
   push.

Prefer a registry record when one exists: if the PI (or labx_admin) creates
`hc/labxManage/Award/<slug>/award.yaml` with lifecycle.status Final/Published,
the news aggregator picks it up automatically — this template is for awards
that have no registry record, or that the PI wants worded by hand.
