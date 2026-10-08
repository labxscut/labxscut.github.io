---
title: Engage
description: "Contact LabX about research opportunities."
permalink: /engage/
redirect_from: /join/
nav:
  order: 7
  tooltip: Contact the lab
---

# Engage with LabX

## Postdoctoral, PhD, and MS opportunities

{% include intro.html value=site.data.intros.engage.students %}

## Research support and partnerships

{% include intro.html value=site.data.intros.engage.themes %}

{% for theme in site.data.research %}
- **{{ theme.title }}** — {{ theme.summary | strip }}
{% endfor %}

{% include intro.html value=site.data.intros.engage.partnerships %}

## Funding support

{% include intro.html value=site.data.intros.engage.funding %}

## Contact

{% include intro.html value=site.data.intros.engage.contact %}

- **Email** · [{{ site.links.email }}](mailto:{{ site.links.email }})
- **School** · {{ site.data.identity.affiliation.unit_en }}, {{ site.data.identity.affiliation.university_en }}
- **Address** · {{ site.data.identity.affiliation.address_en }}
