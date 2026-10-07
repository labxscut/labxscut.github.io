---
title: LabX
description: "LabX is an AI-for-Science group at the School of Mathematics, South China University of Technology."
---

# AI for Science

{% include intro.html value=site.data.intros.home.hero %}

{% include button.html text="Explore our research" link="about/" icon="fa-solid fa-arrow-right" %}
{% include button.html text="Meet the team" link="team/" icon="fa-solid fa-users" %}

<!-- section break -->

## Latest news

{% for item in site.data.news limit:4 %}
- **{{ item.date }}** — {% if item.url %}[{{ item.text }}]({{ item.url }}){% else %}{{ item.text }}{% endif %}
{% endfor %}

<!-- section break -->

## Research

{% include intro.html value=site.data.intros.home.research %}

{% for theme in site.data.research %}
### {{ theme.title }}

{{ theme.summary }}

{% endfor %}

{% include button.html text="All research themes" link="about/" icon="fa-solid fa-arrow-right" %}

<!-- section break -->

## Open-source tools

{% include intro.html value=site.data.intros.home.tools %}

{% for tool in site.data.tools limit:3 %}
### [{{ tool.name }}]({{ tool.docs }})

{{ tool.tagline }}. {{ tool.description }}

{% include button.html text="Documentation" link=tool.docs type="docs" style="bare" %}
{% include button.html text="Source code" link=tool.repo type="source" style="bare" %}
{% endfor %}

{% include button.html text="All tools" link="tools/" icon="fa-solid fa-arrow-right" %}
{% include button.html text="Publications" link="publications/" icon="fa-solid fa-arrow-right" %}

<!-- section break -->

## Activities

{% include intro.html value=site.data.intros.home.activities %}

{% if site.data.activities.size > 0 %}
{% for activity in site.data.activities limit:3 %}
- **{{ activity.date }}** — {{ activity.title }}{% if activity.url %} · [Details]({{ activity.url }}){% endif %}
{% endfor %}
{% else %}
No activities have been posted yet.
{% endif %}

{% include button.html text="All activities" link="activities/" icon="fa-solid fa-arrow-right" %}

<!-- section break -->

## News

{% include intro.html value=site.data.intros.home.news %}

{% assign recent_posts = site.posts | sort: "date" | reverse %}
{% if recent_posts.size > 0 %}
{% for post in recent_posts limit:3 %}
- [{{ post.title }}]({{ post.url | relative_url }}) — {{ post.date | date: "%Y-%m-%d" }}
{% endfor %}
{% else %}
No blog posts have been published yet.
{% endif %}

{% include button.html text="Read the news" link="news/" icon="fa-solid fa-arrow-right" %}
