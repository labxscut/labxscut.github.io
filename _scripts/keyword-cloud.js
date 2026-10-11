/*
  Publications "Browse by topic" cloud: clicking a keyword filters the paper
  list to entries whose text contains that term; clicking it again (or "Show
  all") clears the filter. Self-contained - it does not depend on search.js.
*/
{
  const CLOUD = "#labx-cloud";
  const KEYWORD = ".labx-keyword";
  const PAPER = ".labx-paper";

  const setup = () => {
    const cloud = document.querySelector(CLOUD);
    if (!cloud) return;
    const keywords = [...cloud.querySelectorAll(KEYWORD)];
    if (!keywords.length) return;

    // one status line under the cloud
    let status = document.createElement("p");
    status.className = "labx-cloud-status";
    status.hidden = true;
    cloud.insertAdjacentElement("afterend", status);

    const papers = [...document.querySelectorAll(PAPER)];
    // Year headings are h3/h4 whose entire text is a bare 4-digit year.
    const yearHeadings = [...document.querySelectorAll("main h3, main h4")].filter(
      (h) => /^\d{4}$/.test(h.textContent.trim()) && !h.querySelector("a"),
    );
    let active = null;

    const clear = () => {
      active = null;
      keywords.forEach((k) => k.removeAttribute("data-active"));
      papers.forEach((p) => (p.style.display = ""));
      yearHeadings.forEach((h) => (h.style.display = ""));
      status.hidden = true;
    };

    const apply = (term) => {
      let shown = 0;
      papers.forEach((p) => {
        const hit = p.textContent.toLowerCase().includes(term);
        p.style.display = hit ? "" : "none";
        if (hit) shown++;
      });
      // Group each paper under the year heading that precedes it in document
      // order, then hide a heading whose group has no visible paper. Walking
      // in order avoids offset/offsetParent layout pitfalls.
      const order = [...document.querySelectorAll("main h3, main h4, main .labx-paper")];
      const visibleByHeading = new Map();
      let current = null;
      order.forEach((el) => {
        if (el.matches("h3, h4") && /^\d{4}$/.test(el.textContent.trim()) && !el.querySelector("a")) {
          current = el;
          if (!visibleByHeading.has(current)) visibleByHeading.set(current, false);
        } else if (el.classList.contains("labx-paper") && current) {
          if (el.style.display !== "none") visibleByHeading.set(current, true);
        }
      });
      yearHeadings.forEach((h) => {
        h.style.display = visibleByHeading.get(h) ? "" : "none";
      });
      status.hidden = false;
      status.textContent = `${shown} ${shown === 1 ? "entry" : "entries"} match “${term}”. `;
      const reset = document.createElement("a");
      reset.href = CLOUD;
      reset.textContent = "Show all";
      status.append(reset);
    };

    keywords.forEach((k) => {
      k.addEventListener("click", (e) => {
        e.preventDefault();
        const term = k.dataset.term;
        if (active === term) {
          clear();
          return;
        }
        active = term;
        keywords.forEach((x) =>
          x === k ? x.setAttribute("data-active", "") : x.removeAttribute("data-active"),
        );
        apply(term);
      });
    });

    // "Show all" link in the status line
    status.addEventListener("click", (e) => {
      if (e.target.tagName === "A") {
        e.preventDefault();
        clear();
      }
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
  } else {
    setup();
  }
}
