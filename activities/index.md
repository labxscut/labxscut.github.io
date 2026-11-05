---
title: Activities
description: "Seminars, workshops, and other LabX activities."
permalink: /activities/
nav:
  order: 6
  tooltip: Lab activities
---

# Activities

{% include section-banner.html key="activities" %}

{% include intro.html value=site.data.intros.activities.intro %}
{% assign activities = site.data.activities | where_exp: "item", "item.published_on_site != false" | where_exp: "item", "item.published_on_site != 'noshow'" | sort: "date" | reverse %}
{% if activities.size > 0 %}
{% for activity in activities %}
## {{ activity.title }}

{{ activity.date_display | default: activity.date }}{% if activity.location %} · {{ activity.location }}{% endif %}

{{ activity.description }}

{% if activity.url %}[More information]({{ activity.url }}){% endif %}
{% endfor %}
{% else %}
No activities have been posted yet.
{% endif %}
