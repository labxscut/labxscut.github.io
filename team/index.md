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

{% assign sections = "pi:Principal investigator,faculty:Faculty,visiting:Visiting scholars,phd:PhD students,master:Master's students,under:Undergraduate researchers,alumni:Alumni" | split: "," %}
{% for entry in sections %}
  {% assign pair = entry | split: ":" %}
  {% assign group = site.data.people | where: "section", pair[0] %}
  {% if pair[0] == "phd" %}
    {% comment %}
      PI request (frontend.txt team/3): Xiaoyang Wang (wxy) and Zhimin Li (lzm)
      are not shown in the PhD list. A roster `hide: true` marker is the
      permanent home for this decision; the template filter keeps /team/
      correct even before the roster carries it.
    {% endcomment %}
  {% endif %}
  {% assign visible = "" | split: "" %}
  {% for person in group %}
    {% if pair[0] == "phd" %}
      {% if person.nick == "wxy" or person.nick == "lzm" %}{% continue %}{% endif %}
    {% endif %}
    {% assign visible = visible | push: person %}
  {% endfor %}
  {% if visible.size > 0 %}

## {{ pair[1] }}

{% if pair[0] == "alumni" %}
{% include team-alumni.html %}
{% else %}{% for person in visible %}
{% include team-row.html person=person %}

{% endfor %}{% endif %}
  {% endif %}
{% endfor %}
