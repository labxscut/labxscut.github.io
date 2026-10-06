---
title: People
description: "The LabX research team at South China University of Technology."
nav:
  order: 2
  tooltip: Meet the team
---

# People

LabX is led by {{ site.data.identity.pi.name_en }} ({{ site.data.identity.pi.name_zh }})
at the School of Mathematics, South China University of Technology. Personal
pages link from current members' names. Contact details are not published here.

{% assign sections = "pi:Principal investigator,faculty:Faculty,phd:PhD students,master:Master's students,under:Undergraduate researchers,alumni:Alumni and collaborators" | split: "," %}
{% for entry in sections %}
  {% assign pair = entry | split: ":" %}
  {% assign group = site.data.people | where: "section", pair[0] %}
  {% if group.size > 0 %}

## {{ pair[1] }}

{% for person in group %}
{% if person.has_page %}[**{{ person.name_en }}**](/{{ person.nick }}/){% else %}**{{ person.name_en }}**{% endif %}{% if person.name_zh %} · {{ person.name_zh }}{% endif %} — {{ person.role }}{% if person.start_year %} ({{ person.start_year }}{% if person.end_year %}–{{ person.end_year }}{% endif %}){% endif %}{% if person.affiliation %} · {{ person.affiliation }}{% endif %}{% if person.github %} · [GitHub](https://github.com/{{ person.github }}){% endif %}

{% endfor %}
  {% endif %}
{% endfor %}
