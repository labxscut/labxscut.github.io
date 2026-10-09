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
<div class="labx-news" markdown="1">

{% for item in items %}
- <span class="labx-news-date">{{ item.date_display | default: item.date }}</span> {% if item.url %}[{{ item.text }}]({{ item.url }}){% else %}{{ item.text }}{% endif %}
{% endfor %}

</div>
{% else %}
No news has been posted yet.
{% endif %}
