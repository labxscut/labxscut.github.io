---
title: Tools
description: "Open-source software from the LabX research group."
permalink: /tools/
nav:
  order: 4
  tooltip: Research software
---

# Tools

{% include intro.html value=site.data.intros.tools.intro %}

<div class="labx-tools-grid">

{% for tool in site.data.tools %}
<article class="labx-tool" markdown="1">

<div class="labx-tool-head">
{% if tool.logo %}<img class="labx-tool-logo" src="{{ tool.logo }}" alt="">{% endif %}
<div>

<h2 id="{{ tool.key | slugify }}">{{ tool.name }}</h2>

<span class="labx-tool-tagline">{{ tool.tagline }}</span>

</div>
</div>

{{ tool.description }}

{% assign version = tool.version | default: "" | strip %}
{% unless version == "" %}
<p>Version: {{ version }}</p>
{% endunless %}

{% comment %}
  People behind the tool: catalog maintainers first, then any lab first author
  of the tool's own papers who is not already listed. Names link to the
  member's /team/<nick>/ page when they have one.
{% endcomment %}
{% assign by = "" | split: "" %}
{% assign seen = ",," %}
{% for nick in tool.maintainers %}
  {% assign person = site.data.people | where: "nick", nick | first %}
  {% if person and seen contains ("," | append: nick | append: ",") == false %}
    {% assign by = by | push: person %}
    {% assign seen = seen | append: nick | append: "," %}
  {% endif %}
{% endfor %}
{% for slug in tool.papers %}
  {% assign paper = site.data.publications | where: "slug", slug | first %}
  {% assign first = paper.authors | first %}
  {% if first.nick and seen contains ("," | append: first.nick | append: ",") == false %}
    {% assign person = site.data.people | where: "nick", first.nick | first %}
    {% if person %}
      {% assign by = by | push: person %}
      {% assign seen = seen | append: first.nick | append: "," %}
    {% endif %}
  {% endif %}
{% endfor %}
{% if by.size > 0 %}
<p class="labx-tool-by">Built by
  {%- for person in by -%}
    {%- if person.has_page -%}<a href="/team/{{ person.nick }}/">{{ person.name_en }}</a>{%- else -%}{{ person.name_en }}{%- endif -%}
    {%- unless forloop.last -%}, {% endunless -%}
  {%- endfor -%}
</p>
{% endif %}

<div class="labx-tool-links">
{% if tool.docs and tool.docs != tool.repo %}<a href="{{ tool.docs }}">Service</a>{% endif %}
{% if tool.repo %}<a href="{{ tool.repo }}">Repository</a>{% endif %}
{% if tool.client %}<a href="{{ tool.client }}">API client</a>{% endif %}
{% if tool.docs and tool.docs != tool.repo %}<a href="{{ tool.docs }}">Documentation</a>{% endif %}
</div>

{% include tool-papers.html papers=tool.papers %}

</article>
{% endfor %}

</div>
