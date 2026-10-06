---
title: Tools
description: "Open-source software from the LabX research group."
nav:
  order: 4
  tooltip: Research software
---

# Tools

Open-source software from the group. Documentation remains in each project's
own site and is updated in place.

{% for tool in site.data.tools %}
## [{{ tool.name }}]({{ tool.docs }})

**{{ tool.tagline }}**

{{ tool.description }}

{% if tool.version %}Version: {{ tool.version }} · {% endif %}{{ tool.language }}{% if tool.license %} · {{ tool.license }}{% endif %}

{% include button.html text="Documentation" link=tool.docs type="docs" style="bare" %}
{% include button.html text="GitHub repository" link=tool.repo type="source" style="bare" %}
{% if tool.paper %}
  {% assign paper = site.data.publications | where: "slug", tool.paper | first %}
  {% if paper %}{% include button.html text="Associated paper" link=paper.url type="paper" style="bare" %}{% endif %}
{% endif %}
{% endfor %}
