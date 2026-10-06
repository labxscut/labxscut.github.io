---
title: Opportunities
description: "Contact LabX about research opportunities."
nav:
  order: 8
  tooltip: Contact the lab
---

# Opportunities at LabX

## Postdoctoral, PhD, and MS opportunities

We welcome inquiries from prospective postdoctoral researchers, PhD students,
and master's students interested in our research. Availability depends on
current projects, supervision capacity, and funding; this page does not imply
that a funded position is open. Please email a brief introduction, CV, and
research interests to [{{ site.links.email }}](mailto:{{ site.links.email }}).

## Research support and partnerships

We welcome conversations with agencies and organizations interested in
supporting collaborative research in:

{% for theme in site.data.research %}
- **{{ theme.title }}** — {{ theme.summary | strip }}
{% endfor %}

Potential partners can contact us at
[{{ site.links.email }}](mailto:{{ site.links.email }}) to discuss a research
question, possible collaboration, and support needs.

LabX is based in the School of Mathematics at South China University of
Technology, Guangzhou.
