---
title: News
description: "Notes and updates from the LabX group."
permalink: /blog/
nav:
  order: 1
  tooltip: Lab notes
---

# News

{% assign posts = site.posts | sort: "date" | reverse %}
{% if posts.size > 0 %}
{% for post in posts %}
{% include post-excerpt.html lookup=post.slug %}
{% endfor %}
{% else %}
No blog posts have been published yet.
{% endif %}
