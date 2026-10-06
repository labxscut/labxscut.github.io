---
title: Research
description: "Research themes at LabX."
nav:
  order: 3
  tooltip: Research themes
---

# Research

We develop computational methods for biological and clinical data, with a focus
on transparent, reproducible analysis.

{% for theme in site.data.research %}
## {{ theme.title }}

{{ theme.summary }}

{% if theme.keywords.size > 0 %}**Topics:** {{ theme.keywords | join: " · " }}{% endif %}
{% endfor %}
