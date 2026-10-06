---
title: Publications
description: "Published research from the LabX group."
nav:
  order: 5
  tooltip: Published research
---

# Publications

{{ site.data.publications | size }} published papers. Work still in preparation
or under review is not listed.

{% assign years = site.data.publications | map: "year" | uniq | sort | reverse %}
{% for year in years %}
## {{ year }}

{% assign papers = site.data.publications | where: "year", year %}
{% for paper in papers %}
<article class="labx-paper" id="{{ paper.slug }}">

### {% if paper.url %}[{{ paper.title }}]({{ paper.url }}){% else %}{{ paper.title }}{% endif %}

{% for author in paper.authors %}{% assign person = site.data.people | where: "nick", author.nick | first %}{% if person and person.has_page %}[{{ author.name }}](/{{ author.nick }}/){% else %}{{ author.name }}{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %}

**{{ paper.venue }}** · {{ paper.year }}{% if paper.doi %} · [doi:{{ paper.doi }}](https://doi.org/{{ paper.doi }}){% endif %}{% if paper.repo %} · [Code]({{ paper.repo }}){% endif %}

</article>
{% endfor %}
{% endfor %}
