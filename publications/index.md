---
title: Publications
description: "Published and accepted research from the LabX group."
permalink: /publications/
nav:
  order: 5
  tooltip: Publications
---

# Publications

{% include section-banner.html key="publications" %}

{% comment %}
  published_on_site: noshow (or false) drops a record that is still in the data
  file. The filter is the listing gate on this build; no generator has to run
  first. Meeting abstracts use the same term.
{% endcomment %}
{% assign publications = site.data.publications | where_exp: "paper", "paper.published_on_site != false" | where_exp: "paper", "paper.published_on_site != 'noshow'" %}
{% assign abstracts = site.data.abstracts | where_exp: "paper", "paper.published_on_site != false" | where_exp: "paper", "paper.published_on_site != 'noshow'" %}
{% assign lead = "" | split: "" %}
{% assign collaborative = "" | split: "" %}
{% assign chapters = "" | split: "" %}
{% assign accepted = "" | split: "" %}
{% for paper in publications %}
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
{% assign published_count = publications | size | minus: accepted.size %}
{% assign intros = site.data.intros.publications %}
{% include intro.html value=intros.intro published=published_count accepted=accepted.size %}

{% if site.data.keywords.size > 0 %}
## Browse by topic

<div class="labx-cloud" id="labx-cloud">
{% for kw in site.data.keywords -%}
{%- if kw.count >= 12 -%}{%- assign lvl = "xl" -%}
{%- elsif kw.count >= 8 -%}{%- assign lvl = "lg" -%}
{%- elsif kw.count >= 5 -%}{%- assign lvl = "md" -%}
{%- else -%}{%- assign lvl = "sm" -%}
{%- endif -%}
{%- comment -%}
  Jump to the first paper that carries the term. `kw.slugs` comes from
  gen_keywords.py and holds publication/abstract slugs, which publication-list.html
  renders as anchors on this page; a term with no resolvable slug stays plain text
  rather than linking to a dead anchor.
{%- endcomment -%}
{%- assign target = "" -%}
{%- for slug in kw.slugs -%}
  {%- if target == "" -%}
    {%- assign match = publications | where: "slug", slug | first -%}
    {%- unless match -%}{%- assign match = abstracts | where: "slug", slug | first -%}{%- endunless -%}
    {%- if match -%}{%- assign target = slug | slugify -%}{%- endif -%}
  {%- endif -%}
{%- endfor -%}
{%- if target != "" -%}
<a class="labx-keyword labx-keyword-{{ lvl }}" href="#{{ target }}" data-term="{{ kw.term | downcase }}" data-tooltip="{{ kw.count }} papers">{{ kw.term }}</a>
{%- else -%}
<span class="labx-keyword labx-keyword-{{ lvl }}" data-term="{{ kw.term | downcase }}" data-tooltip="{{ kw.count }} papers">{{ kw.term }}</span>
{%- endif -%}
{% endfor -%}
</div>
{% endif %}

## Lead Papers

{% include intro.html value=intros.lead %}
{% include publication-list.html papers=lead lead=true track="lead" %}

## Collaborative Papers

{% include intro.html value=intros.collaborative %}
{% include publication-list.html papers=collaborative track="collaborative" %}

{% if chapters.size > 0 %}
## Book Chapters

{% include intro.html value=intros.book_chapters %}
{% include publication-list.html papers=chapters track="chapters" %}
{% endif %}

{% if abstracts.size > 0 %}
## Conference Abstracts and Posters

Meeting abstracts and posters, newest first. These are not counted as full
papers.

{% include publication-list.html papers=abstracts track="abstracts" %}
{% endif %}