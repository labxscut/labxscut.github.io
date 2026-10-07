# LabX website content record

This is the structured owner/agent handoff for research themes and verified
website content. It is internal planning material, not a Jekyll data file.
When content is approved for the site, copy or transform it into the relevant
`_data/*.yml` source and check that publication IDs match
`_data/publications.yml`. Keep private contact details, credentials, student
records, and access tokens out of this file.

Use YAML: it remains readable in reviews while representing ordered lists,
short narratives, and relationships between people, papers, tools, and
courses. Replace `TODO` values with verified information or omit that
optional record; never fill gaps by guessing.

```yaml
schema_version: 1
repository: labxscut/labxscut.github.io

research_directions:
  - key: ai-theory
    title: AI theory and learning methodology
    summary: >-
      We study the principles behind reliable learning: generalization bounds,
      domain transfer under distribution shift, hierarchical learning, and
      multi-model and multimodal learning.
    keywords:
      - learning bounds
      - domain transfer
      - distribution shift
      - hierarchical learning
      - multi-model learning
      - multimodal learning
    selected_papers:
      - publication: ChenICML25DshiftShort
        narrative: >-
          Develops an estimable learning bound that unifies covariate and
          concept shift, connecting distribution-shift analysis with
          generalization.

  - key: biomedical-ai
    title: AI for biomedical sciences
    summary: >-
      We develop AI methods for enzyme-function prediction, single-cell
      genomics, metagenomic and phylogenomic analysis, and clinical data.
    keywords:
      - enzyme function prediction
      - single-cell genomics
      - multi-omics
      - metagenomics
      - phylogenomics
      - clinical sciences
    selected_papers:
      - publication: DuanISBRA2025EnzHier
        narrative: >-
          Integrates multi-scale protein-sequence features with hierarchical
          contrastive learning to predict enzyme function.
      - publication: Duan2025sxSNF
        narrative: >-
          Combines similarity-network fusion with deep graph learning to
          integrate multimodal single-cell measurements.
      - publication: Feishu-2023-Ksak-A-high-throughput-tool-for-alignment-free
        narrative: >-
          Presents a high-throughput alignment-free phylogenetics tool,
          relevant to scalable analysis of microbial sequence data.
      - publication: YuHGGadv2025MtagHF
        narrative: >-
          Uses multi-trait genome-wide analysis to identify heart-failure risk
          loci and candidate drugs.
      - publication: ChangTCBB2025UGESdeng
        narrative: >-
          Combines genetic and epigenetic signals with hierarchical learning
          to predict breast-cancer intrinsic subtypes from DNA-level
          multi-omics.

  - key: materials-and-frontiers
    title: AI for materials science and emerging fields
    summary: >-
      We aim to extend AI-for-science methods to materials science and other
      cutting-edge research fields, in collaboration with domain experts.
    keywords:
      - materials science
      - scientific machine learning
      - emerging research fields
    selected_papers: []
    collection_note: >-
      Add only verified, relevant work. The current publication registry has
      no confirmed materials-science example.

people:
  # Public-safe information only. Do not put private contact information,
  # student records, credentials, or unapproved biographical details here.
  - id: TODO-roster-nick
    display_name: TODO-approved public name
    name_zh: TODO-or-omit
    role: TODO-current public role
    affiliation: TODO-public affiliation
    short_bio: TODO-verified concise biography
    research_keywords: [TODO]
    profile_links:
      cv_url: TODO-direct-link-to-verified-public-PDF-or-omit
      cv_repository_url: TODO-public-GitHub-repository-named-for-this-person-or-omit
      orcid: TODO-verified-url-or-omit
      scholar: TODO-verified-url-or-omit
      github: TODO-verified-url-or-omit
      website: TODO-public-url-or-omit
    profile_material:
      publications: [TODO-publication-ids]
      tools: [TODO-tool-ids]
      courses: [TODO-course-ids]
    verification_source: TODO-owner-or-public-source

publications:
  # Preserve the registry slug as the stable ID. Include only verified
  # publication metadata and state the publication status accurately.
  - id: TODO-stable-registry-slug
    title: TODO-exact-published-title
    authors: [TODO-person-ids-or-author-names]
    venue: TODO-venue
    year: TODO-year
    status: TODO-Published-Final-Accepted-or-other-verified-status
    doi: TODO-doi-or-omit
    url: TODO-stable-public-url
    research_directions: [ai-theory]
    keywords: [TODO]
    short_narrative: TODO-factual-one-or-two-sentence-summary
    verification_source: TODO-publisher-doi-or-owner-record

tools:
  - id: TODO-stable-tool-key
    name: TODO-public-tool-name
    summary: TODO-what-the-tool-does-and-who-it-serves
    keywords: [TODO]
    maintainers: [TODO-person-ids]
    repository_url: TODO-public-repository
    documentation_url: TODO-public-documentation
    publication_ids: [TODO-registry-slugs]
    research_directions: [biomedical-ai]
    verification_source: TODO-owner-or-public-repository

courses:
  - id: TODO-stable-course-key
    title: TODO-public-course-title
    instructors: [TODO-person-ids]
    term: TODO-term-and-year
    short_description: TODO-public-course-summary
    keywords: [TODO]
    materials:
      - provider: GitHub
        label: Course materials
        url: TODO-course-repository-or-resource
      - provider: Ulearning
        label: Course page
        url: TODO-course-page
    access_note: >-
      Access is controlled by the hosting provider. Record links only; never
      include credentials or copy restricted course materials into this repo.
    verification_source: TODO-course-owner-or-official-course-page
```

## Authoring and publication rules

- Research-direction keys are stable IDs; cite papers by their exact
  `_data/publications.yml` slug, not by title text alone.
- Keep each narrative short, specific, and supported by the paper itself.
  Distinguish a direct application from related enabling methodology.
- Select representative papers rather than copying the entire bibliography.
  This selection is not a claim that the PI's Google Scholar record is
  complete.
- Only list materials-science or other emerging-field examples after their
  topic and LabX contribution have been verified. Until then, keep the
  direction as an aspiration and leave its selected-paper list empty.
- People records use approved public names and facts; use the existing
  roster/generator for member pages and do not expose private roster fields.
- For a CV, check for a public GitHub repository named after the person's
  public nick, then verify that it contains their intended CV PDF. Do not
  infer a repository, owner, filename, or permission. Add the verified direct
  PDF URL as `cv_url` and repository URL as `cv_repository_url` to
  `_data/member_profiles.yml`; the profile panel and CV tab use that curated
  URL. The CV should appear in the left profile panel only after its public PDF
  link has been verified.
- Tools and courses link to their authoritative repositories/platforms.
  Hosting providers control access; do not mirror restricted resources.
- Keep canonical website data in `_data/research.yml`, `_data/people.yml`,
  `_data/publications.yml`, `_data/tools.yml`, and
  `_data/member_teaching.yml`. This file is the readable intake/curation
  record; do not hand-edit generated files as a substitute.
