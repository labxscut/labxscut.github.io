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

{% include intro.html value=site.data.intros.about.intro %}

{% for theme in site.data.research %}
## {{ theme.title }}

{{ theme.summary }}

{% if theme.keywords.size > 0 %}
<div class="labx-tags">
{% for kw in theme.keywords %}<span class="labx-tag">{{ kw }}</span>{% endfor %}
</div>
{% endif %}

{% if theme.selected_papers.size > 0 %}

**Selected work**

<div class="labx-left" markdown="1">

{% for selected in theme.selected_papers %}
{% assign paper = site.data.publications | where: "slug", selected.slug | first %}
{% if paper %}
- {% if paper.url != "" %}[{{ paper.title }}]({{ paper.url }}){% else %}{{ paper.title }}{% endif %} ({{ paper.year }}). {{ selected.narrative }}
{% endif %}
{% endfor %}

</div>
{% elsif theme.evidence_note %}

{{ theme.evidence_note }}
{% endif %}
{% endfor %}
