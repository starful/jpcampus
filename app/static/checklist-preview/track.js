/* GA4 click + page view for checklist preview (standalone HTML). */
(function () {
  var GA_ID = "G-EDJL0618LL";
  var lang = document.documentElement.getAttribute("lang") || "";
  var page =
    document.body.getAttribute("data-preview-page") ||
    (location.pathname.split("/").pop() || "unknown");

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    dataLayer.push(arguments);
  }
  window.gtag = gtag;

  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
  s.onload = function () {
    gtag("js", new Date());
    gtag("config", GA_ID);
    gtag("event", "checklist_preview_view", {
      event_category: "engagement",
      event_label: page,
      language: lang,
      page_path: location.pathname,
      transport_type: "beacon"
    });
  };
  document.head.appendChild(s);

  document.addEventListener(
    "click",
    function (event) {
      var target = event.target.closest("[data-track]");
      if (!target || typeof window.gtag !== "function") return;
      var action = target.getAttribute("data-track");
      var label = target.getAttribute("data-track-label") || "";
      var trackLang = target.getAttribute("data-track-lang") || lang;
      var href = target.getAttribute("href") || "";
      window.gtag("event", action, {
        event_category: "engagement",
        event_label: label,
        language: trackLang,
        link_url: href,
        preview_page: page,
        transport_type: "beacon"
      });
    },
    true
  );
})();
