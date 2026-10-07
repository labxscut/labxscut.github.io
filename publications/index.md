---
title: Publications
description: "Published and accepted research from the LabX group."
permalink: /publications/
nav:
  order: 5
  tooltip: Publications
---

# Publications

{% assign published = "" | split: "" %}
{% assign accepted = "" | split: "" %}
{% for paper in site.data.publications %}
  {% if paper.status == "Accept" or paper.status == "Accepted" %}
    {% assign accepted = accepted | push: paper %}
  {% else %}
    {% assign published = published | push: paper %}
  {% endif %}
{% endfor %}
{% include intro.html value=site.data.intros.publications.intro published=published.size accepted=accepted.size %}

## Published

{% assign papers = published %}
{% assign years = papers | map: "year" | uniq | sort | reverse %}
{% for year in years %}
## {{ year }}

{% assign year_papers = papers | where: "year", year %}
{% for paper in year_papers %}
<article class="labx-paper" id="{{ paper.slug | slugify }}" markdown="1">

### {% if paper.url != "" %}[{{ paper.title }}]({{ paper.url }}){% else %}{{ paper.title }}{% endif %}

{% for author in paper.authors %}{% assign person = site.data.people | where: "nick", author.nick | first %}{% if person and person.has_page %}[{{ author.name }}](/team/{{ author.nick }}/){% else %}{{ author.name }}{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %}

**{{ paper.venue }}** · {{ paper.year }}{% if paper.doi != "" %} · [doi:{{ paper.doi }}](https://doi.org/{{ paper.doi }}){% endif %}{% if paper.repo != "" %} · [Code]({{ paper.repo }}){% endif %}
{% if paper.tools.size > 0 %}{% for key in paper.tools %}{% assign tool = site.data.tools | where: "key", key | first %}{% if tool %} · [{{ tool.name }}](/tools/#{{ tool.key | slugify }}){% endif %}{% endfor %}{% endif %}

</article>
{% endfor %}
{% endfor %}

{% if accepted.size > 0 %}
## Accepted

{% assign years = accepted | map: "year" | uniq | sort | reverse %}
{% for year in years %}
### {{ year }}
{% assign year_papers = accepted | where: "year", year %}
{% for paper in year_papers %}
<article class="labx-paper" id="{{ paper.slug | slugify }}" markdown="1">

### {% if paper.url != "" %}[{{ paper.title }}]({{ paper.url }}){% else %}{{ paper.title }}{% endif %}

{% for author in paper.authors %}{% assign person = site.data.people | where: "nick", author.nick | first %}{% if person and person.has_page %}[{{ author.name }}](/team/{{ author.nick }}/){% else %}{{ author.name }}{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %}

**{{ paper.venue }}** · {{ paper.year }} <span class="labx-status">Accepted</span>{% if paper.doi != "" %} · [doi:{{ paper.doi }}](https://doi.org/{{ paper.doi }}){% endif %}
{% if paper.tools.size > 0 %}{% for key in paper.tools %}{% assign tool = site.data.tools | where: "key", key | first %}{% if tool %} · [{{ tool.name }}](/tools/#{{ tool.key | slugify }}){% endif %}{% endfor %}{% endif %}

</article>
{% endfor %}
{% endfor %}
{% endif %}
