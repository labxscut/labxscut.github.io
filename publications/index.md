---
title: Publications
description: "Published and accepted research from the LabX group."
permalink: /publications/
nav:
  order: 5
  tooltip: Publications
---

# Publications

{% assign lead = "" | split: "" %}
{% assign collaborative = "" | split: "" %}
{% assign chapters = "" | split: "" %}
{% assign accepted = "" | split: "" %}
{% for paper in site.data.publications %}
  {% if paper.status == "Accept" or paper.status == "Accepted" %}
    {% assign accepted = accepted | push: paper %}
  {% endif %}
  {% case paper.pi_track %}
    {% when "lead" %}
      {% assign lead = lead | push: paper %}
    {% when "book-chapter" %}
      {% assign chapters = chapters | push: paper %}
    {% else %}
      {% assign collaborative = collaborative | push: paper %}
  {% endcase %}
{% endfor %}
{% assign published_count = site.data.publications | size | minus: accepted.size %}
{% assign intros = site.data.intros.publications %}
{% include intro.html value=intros.intro published=published_count accepted=accepted.size %}

## Team Lead Papers

{% include intro.html value=intros.lead %}
{% include publication-list.html papers=lead %}

## Collaborative Papers

{% include intro.html value=intros.collaborative %}
{% include publication-list.html papers=collaborative %}

{% if chapters.size > 0 %}
## Book Chapters

{% include intro.html value=intros.book_chapters %}
{% include publication-list.html papers=chapters %}
{% endif %}