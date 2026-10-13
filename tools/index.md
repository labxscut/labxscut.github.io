---
title: Tools
description: "Open-source software from the LabX research group."
permalink: /tools/
nav:
  order: 4
  tooltip: Research software
---

# Tools

{% include section-banner.html key="tools" %}

{% include intro.html value=site.data.intros.tools.intro %}

<div class="labx-tools-grid">

{% for tool in site.data.tools %}
<article class="labx-tool" markdown="1">

<div class="labx-tool-head">
{% if tool.logo %}<img class="labx-tool-logo" src="{{ tool.logo }}" alt="">{% endif %}
<div>

<h2 id="{{ tool.key | slugify }}">{{ tool.name }}</h2>

<span class="labx-tool-tagline">{{ tool.tagline }}</span>

</div>
</div>

{{ tool.description }}

{% assign version = tool.version | default: "" | strip %}
{% unless version == "" %}
<p>Version: {{ version }}</p>
{% endunless %}

{% comment %}
  People behind the tool: catalog maintainers first, then any lab first author
  of the tool's own papers who is not already listed. Names link to the
  member's /team/<nick>/ page when they have one.
{% endcomment %}
{% assign nicks = tool.maintainers %}
{% for slug in tool.papers %}
  {% assign paper = site.data.publications | where: "slug", slug | first %}
  {% assign first = paper.authors | first %}
  {% if first.nick != "" and first.nick != nil %}
    {% assign nicks = nicks | push: first.nick %}
  {% endif %}
{% endfor %}
{% assign nicks = nicks | uniq %}
{% assign by = "" | split: "" %}
{% for nick in nicks %}
  {% assign person = site.data.people | where: "nick", nick | first %}
  {% if person %}{% assign by = by | push: person %}{% endif %}
{% endfor %}
{% if by.size > 0 %}
<p class="labx-tool-by">Built by {% for person in by %}{% if person.has_page %}<a href="/team/{{ person.nick }}/">{{ person.name_en }}</a>{% else %}{{ person.name_en }}{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %}</p>
{% endif %}

{% comment %}
  A tool whose repository is private must not be linked: /tools/ is public, so
  the link 404s for every visitor. `_data/tools.yml` marks those with
  `private: true`. The catalog entry itself stays (the tool is real work and its
  papers still link), only the unreachable URLs are suppressed. A `docs` URL that
  differs from `repo` is a separate hosted site and stays linkable, and
  `benchmarks` are extra public repositories (e.g. a review paper's companion
  data/code), so either keeps the links block alive on its own. `.size > 0`
  rather than a bare truthiness test because Liquid treats an empty array as
  truthy, which would emit an empty links div.
{% endcomment %}
{% assign repo_public = true %}
{% if tool.private %}{% assign repo_public = false %}{% endif %}
{% assign docs_public = repo_public %}
{% if tool.docs != tool.repo %}{% assign docs_public = true %}{% endif %}
{% comment %}
  A hosted service can carry a `documentation` URL distinct from its `docs`
  homepage (sxEnzHier: the EnzHire service root is the predictor, /docs is its
  manual). `docs` alone keeps both labels pointing at the same place, which is
  what the site-hosted docs pages (sxLaep, DeepLB, sxSNF) want.
{% endcomment %}
{% assign doc_url = tool.documentation | default: tool.docs %}
{% if repo_public or docs_public or tool.client or tool.benchmarks.size > 0 %}
<div class="labx-tool-links">
{% if docs_public and tool.docs and tool.docs != tool.repo %}<a href="{{ tool.docs }}">Service</a>{% endif %}
{% if repo_public and tool.repo %}<a href="{{ tool.repo }}">Repository</a>{% endif %}
{% if tool.client %}<a href="{{ tool.client }}">API client</a>{% endif %}
{% if docs_public and doc_url and doc_url != tool.repo %}<a href="{{ doc_url }}">Documentation</a>{% endif %}
{% for extra in tool.benchmarks %}<a href="{{ extra.url }}">{{ extra.label | default: "Benchmark" }}</a>{% endfor %}
</div>
{% elsif tool.repo %}
<p class="labx-tool-private">Source code is not publicly released.</p>
{% endif %}

{% include tool-papers.html papers=tool.papers %}

</article>
{% endfor %}

</div>
