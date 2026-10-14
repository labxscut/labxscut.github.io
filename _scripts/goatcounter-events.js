/*
  GoatCounter click events.

  Sends three kinds of custom event to GoatCounter, whose counter script is
  emitted by _includes/analytics.html:

    keyword:<term>          a "Browse by topic" term was clicked
    paper:<file>.pdf        a same-origin PDF (e.g. /papers/*.pdf) was opened
    outbound:<host><path>   a link leaving this site was followed

  Everything here is inert when analytics are not configured: analytics.html
  only writes the counter <script> when `goatcounter:` is set in _config.yml,
  so without it no event is queued or sent.

  The counter script loads `async`, so window.goatcounter.count may not exist
  yet when a click happens; events are queued and flushed by the poll interval
  GoatCounter documents. Event names double as the path and must not start with
  "/", and `no_session` makes every click count instead of being deduplicated
  within one visitor session.
*/

{
  const POLL_MS = 100;
  const NO_SESSION = true;

  // events recorded before the counter script finished loading
  const pending = [];
  let polling = false;
  let configured = null;

  // analytics.html writes <script data-goatcounter=...> only when configured
  const isConfigured = () => {
    if (configured === null)
      configured = !!document.querySelector("script[data-goatcounter]");
    return configured;
  };

  const counterReady = () =>
    window.goatcounter && typeof window.goatcounter.count === "function";

  const flush = () => {
    while (pending.length) window.goatcounter.count(pending.shift());
  };

  const poll = () => {
    if (polling) return;
    polling = true;
    const timer = setInterval(() => {
      if (!counterReady()) return;
      clearInterval(timer);
      polling = false;
      flush();
    }, POLL_MS);
  };

  const track = (path, title) => {
    const event = { path, title, event: true, no_session: NO_SESSION };
    if (counterReady()) window.goatcounter.count(event);
    else {
      pending.push(event);
      poll();
    }
  };

  // strip a leading "www." so one host does not report as two
  const host = (url) => url.hostname.replace(/^www\./, "");

  // outbound event name: host plus path, without the query string or hash
  const outboundName = (url) => {
    const path = url.pathname.replace(/\/+$/, "");
    return `outbound:${host(url)}${path}`;
  };

  const linkFrom = (target) => {
    if (!(target instanceof Element)) return null;
    return target.closest("a[href], area[href]");
  };

  const keywordFrom = (target) => {
    if (!(target instanceof Element)) return null;
    return target.closest(".labx-keyword");
  };

  // capture phase: count the click even if another handler stops propagation
  document.addEventListener(
    "click",
    (event) => {
      if (!isConfigured()) return;

      // keyword-cloud terms are <a href="#slug"> or a plain <span>, so they
      // are matched before the generic link handling below
      const keyword = keywordFrom(event.target);
      if (keyword) {
        const term = (
          keyword.dataset.term || keyword.textContent
        ).trim().toLowerCase();
        if (term) track(`keyword:${term}`, `Keyword: ${term}`);
        return;
      }

      const link = linkFrom(event.target);
      if (!link) return;

      let url;
      try {
        url = new URL(link.href, location.href);
      } catch {
        return;
      }

      // ignore mailto:/tel:/javascript: and in-page anchors
      if (url.protocol !== "http:" && url.protocol !== "https:") return;
      if (host(url) === host(location) && url.hash) return;

      if (host(url) === host(location)) {
        // ordinary internal navigation is already counted as a pageview;
        // only local documents worth counting separately are the PDFs
        if (!url.pathname.toLowerCase().endsWith(".pdf")) return;
        const file = url.pathname.split("/").pop();
        track(`paper:${file}`, `PDF: ${url.pathname}`);
        return;
      }

      track(outboundName(url), `Outbound: ${url.href}`);
    },
    true,
  );
}
