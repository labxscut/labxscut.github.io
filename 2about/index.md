---
title: About
description: "Research themes at LabX."
permalink: /about/
redirect_from: /research/
nav:
  order: 2
  tooltip: Research themes
---

# About

We develop computational methods for biological and clinical data, with a focus
on transparent, reproducible analysis.

{% for theme in site.data.research %}
## {{ theme.title }}

{{ theme.summary }}

{% if theme.keywords.size > 0 %}**Topics:** {{ theme.keywords | join: " · " }}{% endif %}
{% endfor %}
