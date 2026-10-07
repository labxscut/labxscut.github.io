---
title: Team
description: "The LabX research team at South China University of Technology."
permalink: /team/
redirect_from: /people/
nav:
  order: 3
  tooltip: Meet the team
---

# Team

{% include intro.html value=site.data.intros.team.intro %}

{% assign sections = "pi:Principal investigator,faculty:Faculty,phd:PhD students,master:Master's students,under:Undergraduate researchers,alumni:Alumni,collaborator:Collaborators,visiting:Visiting scholars" | split: "," %}
{% for entry in sections %}
  {% assign pair = entry | split: ":" %}
  {% assign group = site.data.people | where: "section", pair[0] %}
  {% if group.size > 0 %}

## {{ pair[1] }}

{% for person in group %}
{% if person.has_page %}[**{{ person.name_en }}**](/team/{{ person.nick }}/){% else %}**{{ person.name_en }}**{% endif %}{% if person.name_zh %} · {{ person.name_zh }}{% endif %} — {{ person.role }}{% if person.years %} ({{ person.years }}){% endif %}{% if person.affiliation %} · {{ person.affiliation }}{% endif %}{% if person.now %} · now {{ person.now }}{% endif %}{% if person.github %} · [GitHub](https://github.com/{{ person.github }}){% endif %}

{% endfor %}
  {% endif %}
{% endfor %}
