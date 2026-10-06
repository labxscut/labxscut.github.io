---
title: Activities
description: "Seminars, workshops, and other LabX activities."
permalink: /activities/
nav:
  order: 6
  tooltip: Lab activities
---

# Activities

{% if site.data.activities.size > 0 %}
{% assign activities = site.data.activities | sort: "date" | reverse %}
{% for activity in activities %}
## {{ activity.title }}

{{ activity.date }}{% if activity.location %} · {{ activity.location }}{% endif %}

{{ activity.description }}

{% if activity.url %}[More information]({{ activity.url }}){% endif %}
{% endfor %}
{% else %}
No activities have been posted yet.
{% endif %}
