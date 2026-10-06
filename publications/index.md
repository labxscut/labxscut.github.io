---
title: Publications
description: "Published and accepted research from the LabX group."
nav:
  order: 5
  tooltip: Publications
---

# Publications

{% assign published = site.data.publications | where_exp: "paper", "paper.status != 'Accept' and paper.status != 'Accepted'" %}
{% assign accepted = site.data.publications | where_exp: "paper", "paper.status == 'Accept' or paper.status == 'Accepted'" %}
{{ published.size }} published and {{ accepted.size }} accepted records, deduplicated
from the LabX paper registry. Work in preparation or under review is not listed.
The registry has not been verified as a complete match to Google Scholar; see
[Xia Li's Google Scholar profile]({{ site.data.identity.pi.scholar }}) for the
broader author bibliography.

## Published

{% assign papers = published %}
{% assign years = papers | map: "year" | uniq | sort | reverse %}
{% for year in years %}
## {{ year }}

{% assign year_papers = papers | where: "year", year %}
{% for paper in year_papers %}
<article class="labx-paper" id="{{ paper.slug | slugify }}" markdown="1">

### {% if paper.url != "" %}[{{ paper.title }}]({{ paper.url }}){% else %}{{ paper.title }}{% endif %}

{% for author in paper.authors %}{% assign person = site.data.people | where: "nick", author.nick | first %}{% if person and person.has_page %}[{{ author.name }}](/people/{{ author.nick }}/){% else %}{{ author.name }}{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %}

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

{% for author in paper.authors %}{% assign person = site.data.people | where: "nick", author.nick | first %}{% if person and person.has_page %}[{{ author.name }}](/people/{{ author.nick }}/){% else %}{{ author.name }}{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %}

**{{ paper.venue }}** · {{ paper.year }} <span class="labx-status">Accepted</span>{% if paper.doi != "" %} · [doi:{{ paper.doi }}](https://doi.org/{{ paper.doi }}){% endif %}
{% if paper.tools.size > 0 %}{% for key in paper.tools %}{% assign tool = site.data.tools | where: "key", key | first %}{% if tool %} · [{{ tool.name }}](/tools/#{{ tool.key | slugify }}){% endif %}{% endfor %}{% endif %}

</article>
{% endfor %}
{% endfor %}
{% endif %}
