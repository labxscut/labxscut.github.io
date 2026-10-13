/*
  Live citation checks next to each paper on /publications/.

  GitHub Pages has no server, so the counts cannot be baked into the build
  (they would go stale and every regeneration would churn _data). Instead the
  page asks OpenAlex directly, on load, for every DOI rendered on the page —
  batched into as few requests as the API's URL limits allow (see CHUNK).

  Why OpenAlex: it needs no API key, is explicitly free for all uses, returns
  `Access-Control-Allow-Origin: *` so a static page can fetch it, and its
  `cited_by_count` is a real citation number. Altmetric needs a client
  id/secret and Semantic Scholar rate-limits anonymous batch calls hard
  (HTTP 429 on the first probe), so neither is dependable here.

  Each paper gets:
    · "cited by N" linking to its OpenAlex record (the "website" check),
    · a "Scholar" link running a Google Scholar citation search on the title.
  A DOI OpenAlex does not know (a very recent deposit, or an arXiv DOI it has
  not matched yet) renders nothing rather than a zero, because "0 citations"
  and "not found" are different claims and only the first is checkable.

  OpenAlex lowercases DOIs; matching is therefore case-insensitive. Requests
  are chunked so an over-long URL cannot silently truncate the filter, and a
  failing chunk only costs its own papers.
*/
{
  const CHUNK = 40; // DOIs per request: keeps the filter URL well under limits
  const API = "https://api.openalex.org/works";
  // Polite-pool contact; OpenAlex asks for it and it costs nothing to send.
  const MAILTO = "lcxia@scut.edu.cn";

  const papersWithDoi = () =>
    [...document.querySelectorAll(".labx-paper[data-doi]")].filter(
      (el) => el.dataset.doi.trim(),
    );

  const chunk = (arr, n) => {
    const out = [];
    for (let i = 0; i < arr.length; i += n) out.push(arr.slice(i, i + n));
    return out;
  };

  const fetchCounts = async (dois) => {
    // OpenAlex ORs values WITHIN one filter (doi:A|B|C). Repeating the key
    // (doi:A|doi:B) is an OR *between* filters and the API rejects it with a
    // 400, so the `doi:` prefix appears exactly once.
    const filter = `doi:${dois.join("|")}`;
    const url =
      `${API}?filter=${encodeURIComponent(filter)}` +
      `&per-page=${CHUNK}&select=id,doi,cited_by_count&mailto=${MAILTO}`;
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(`OpenAlex HTTP ${res.status}`);
    const body = await res.json();
    const byDoi = new Map();
    for (const w of body.results || []) {
      // "https://doi.org/10.1109/..." -> "10.1109/..."
      const raw = String(w.doi || "").replace(/^https?:\/\/(dx\.)?doi\.org\//i, "");
      if (!raw) continue;
      byDoi.set(raw.toLowerCase(), {
        count: Number(w.cited_by_count) || 0,
        // Reader-facing page: the stable OpenAlex work ID (…/W2953931274),
        // which is what openalex.org serves to a browser. The id arrives as
        // "https://openalex.org/W…"; keep the bare W-id.
        id: String(w.id || "").replace(/^https?:\/\/openalex\.org\//i, ""),
      });
    }
    return byDoi;
  };

  const scholarUrl = (title) =>
    `https://scholar.google.com/scholar?q=${encodeURIComponent(`"${title}"`)}`;

  const render = (el, rec) => {
    // Inside the markdown="1" <article> the body is two paragraphs: the author
    // list, then the citation line with any tool/announcement links appended on
    // the same line (no blank line between them in publication-list.html). So
    // the LAST <p> is the citation paragraph, and appending inline extends its
    // existing "· … · …" chain instead of starting a new block.
    const paras = el.querySelectorAll("p");
    const target = paras.length ? paras[paras.length - 1] : el;

    const cited = document.createElement("a");
    cited.className = "labx-cite-citedby";
    // Prefer the stable OpenAlex work page (…/W…); fall back to the doi: path
    // only if the API somehow omitted the id.
    cited.href = rec.id
      ? `https://openalex.org/${rec.id}`
      : `https://openalex.org/works/doi:${encodeURIComponent(rec.doi)}`;
    cited.target = "_blank";
    cited.rel = "noopener";
    cited.textContent = `cited by ${rec.count}`;
    cited.title = "Citation count from OpenAlex (opens in a new tab)";

    const title = el.querySelector("h4 a, h3 a") || el.querySelector("h4, h3");
    const scholar = document.createElement("a");
    scholar.className = "labx-cite-scholar";
    scholar.href = scholarUrl(title ? title.textContent : "");
    scholar.target = "_blank";
    scholar.rel = "noopener";
    scholar.textContent = "Scholar";
    scholar.title = "Search this title on Google Scholar (opens in a new tab)";

    target.append(
      document.createTextNode(" · "),
      cited,
      document.createTextNode(" · "),
      scholar,
    );
  };

  const setup = async () => {
    const papers = papersWithDoi();
    if (!papers.length) return;

    // One map across all chunks; a chunk that fails simply contributes nothing.
    const counts = new Map();
    const chunks = chunk(papers.map((p) => p.dataset.doi.trim()), CHUNK);
    const results = await Promise.allSettled(chunks.map(fetchCounts));
    for (const r of results) {
      if (r.status === "fulfilled") {
        for (const [k, v] of r.value) counts.set(k, v);
      }
    }

    let shown = 0;
    for (const el of papers) {
      const doi = el.dataset.doi.trim();
      const rec = counts.get(doi.toLowerCase());
      if (!rec) continue; // unknown to OpenAlex: render nothing, never a false 0
      render(el, { ...rec, doi });
      shown++;
    }

    // A single quiet note so a reader knows the numbers are live, not curated.
    if (shown) {
      const note = document.createElement("p");
      note.className = "labx-citations-note";
      note.textContent =
        `Citation counts are fetched live from OpenAlex for ${shown} ` +
        `${shown === 1 ? "entry" : "entries"} on this page.`;
      const main = document.querySelector("main") || document.body;
      main.append(note);
    }
  };

  const start = () => {
    setup().catch(() => {
      /* network blocked or API down: leave the page exactly as it was */
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
}
