---
title: News
description: "Notes and updates from the LabX group."
permalink: /news/
redirect_from: /blog/
nav:
  order: 1
  tooltip: Lab notes
---

# News

{% include section-banner.html key="news" %}

{% include intro.html value=site.data.intros.news.intro %}
{% assign items = site.data.news | sort: "date" | reverse %}
{%- if items.size > 0 -%}
{%- assign last_year = "" -%}
{%- for item in items -%}
{%- assign shown = item.date_display | default: item.date | append: "" -%}
{%- assign y = shown | slice: 0, 4 -%}
{% if y != last_year %}
## {{ y }}
{% assign last_year = y %}{% endif %}
{% include news-item.html item=item %}
{%- endfor -%}
{%- else -%}
No news has been posted yet.
{%- endif -%}
