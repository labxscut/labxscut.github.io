---
title: News
description: "Notes and updates from the LabX group."
permalink: /news/
redirect_from: /blog/
nav:
  order: 1
  tooltip: Lab notes
---

# News

{% include intro.html value=site.data.intros.news.intro %}
{% assign items = site.data.news | sort: "date" | reverse %}
{% if items.size > 0 %}
{% for item in items %}
- **{{ item.date }}** — {% if item.url %}[{{ item.text }}]({{ item.url }}){% else %}{{ item.text }}{% endif %}
{% endfor %}
{% else %}
No news has been posted yet.
{% endif %}
