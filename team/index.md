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

{% assign sections = "pi:Principal investigator,faculty:Faculty,collaborator:Collaborators,visiting:Visiting scholars,phd:PhD students,master:Master's students,under:Undergraduate researchers,alumni:Alumni" | split: "," %}
{% for entry in sections %}
  {% assign pair = entry | split: ":" %}
  {% assign group = site.data.people | where: "section", pair[0] %}
  {% if group.size > 0 %}

## {{ pair[1] }}

{% if pair[0] == "alumni" %}
{% include team-alumni.html %}
{% else %}{% for person in group %}
{% include team-row.html person=person %}

{% endfor %}{% endif %}
  {% endif %}
{% endfor %}
