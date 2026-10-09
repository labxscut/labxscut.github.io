---
title: LabX
description: "LabX is an AI-for-Science group at the School of Mathematics, South China University of Technology."
---

# AI for Science

<img src="{{ '/images/hero.svg' | relative_url }}" alt="" class="labx-hero-art">

{% include intro.html value=site.data.intros.home.hero %}

{% include button.html text="Explore our research" link="about/" icon="fa-solid fa-arrow-right" %}
{% include button.html text="Meet the team" link="team/" icon="fa-solid fa-users" %}

<!-- section break -->

## Latest news

{% assign latest_news = site.data.news | sort: "date" | reverse %}
<div class="labx-news" markdown="1">

{% for item in latest_news limit:3 %}
- <span class="labx-news-date">{{ item.date_display | default: item.date }}</span> {% if item.url %}[{{ item.text }}]({{ item.url }}){% else %}{{ item.text }}{% endif %}
{% endfor %}

</div>

{% include button.html text="All news" link="news/" icon="fa-solid fa-arrow-right" %}

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

{% if site.data.activities.size > 0 %}
## Activities

{% include intro.html value=site.data.intros.home.activities %}

{% for activity in site.data.activities limit:3 %}
- **{{ activity.date_display | default: activity.date }}** — {{ activity.title }}{% if activity.url %} · [Details]({{ activity.url }}){% endif %}
{% endfor %}

{% include button.html text="All activities" link="activities/" icon="fa-solid fa-arrow-right" %}
{% endif %}

