---
title: Tools
description: "Open-source software from the LabX research group."
permalink: /tools/
nav:
  order: 4
  tooltip: Research software
---

# Tools

{% include intro.html value=site.data.intros.tools.intro %}

{% for tool in site.data.tools %}
<article class="labx-tool" markdown="1">

## {{ tool.name }}

**{{ tool.tagline }}**

{{ tool.description }}

{% assign version = tool.version | default: "" | strip %}
{% assign language = tool.language | default: "" | strip %}
{% assign license = tool.license | default: "" | strip %}
{% unless version == "" and language == "" and license == "" %}
<p>{% if version != "" %}Version: {{ version }}{% endif %}{% if language != "" %}{% if version != "" %} · {% endif %}{{ language }}{% endif %}{% if license != "" %}{% if version != "" or language != "" %} · {% endif %}{{ license }}{% endif %}</p>
{% endunless %}

<div class="labx-tool-links">
{% if tool.docs and tool.docs != tool.repo %}<a href="{{ tool.docs }}">Project / service</a>{% endif %}
{% if tool.repo %}<a href="{{ tool.repo }}">Repository</a>{% endif %}
{% if tool.client %}<a href="{{ tool.client }}">API client</a>{% endif %}
</div>

</article>
{% endfor %}
