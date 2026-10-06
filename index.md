---
title: LabX
description: "LabX is an AI-for-Science group at the School of Mathematics, South China University of Technology."
---

# AI for Science

LabX is a research group in the School of Mathematics at South China University
of Technology. We develop machine-learning methods for genomes, proteins,
single cells, and clinical data, and share our research as open-source tools.

{% include button.html text="Explore our research" link="research/" icon="fa-solid fa-arrow-right" %}
{% include button.html text="Meet the team" link="people/" icon="fa-solid fa-users" %}

<!-- section break -->

## Research

{% for theme in site.data.research %}
### {{ theme.title }}

{{ theme.summary }}

{% endfor %}

{% include button.html text="All research themes" link="research/" icon="fa-solid fa-arrow-right" %}

<!-- section break -->

## Open-source tools

We build software to make our methods and research workflows reusable.

{% for tool in site.data.tools %}
### [{{ tool.name }}]({{ tool.docs }})

{{ tool.tagline }}. {{ tool.description }}

{% include button.html text="Documentation" link=tool.docs type="docs" style="bare" %}
{% include button.html text="Source code" link=tool.repo type="source" style="bare" %}
{% endfor %}

<!-- section break -->

## Latest news

{% for item in site.data.news limit:4 %}
- **{{ item.date }}** — {% if item.url %}[{{ item.text }}]({{ item.url }}){% else %}{{ item.text }}{% endif %}
{% endfor %}

{% include button.html text="All tools" link="tools/" icon="fa-solid fa-arrow-right" %}
{% include button.html text="Publications" link="publications/" icon="fa-solid fa-arrow-right" %}
