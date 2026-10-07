/* Top bar: KO/EN switch + 3 preview pages. No side nav. */
(function () {
  var lang = document.documentElement.getAttribute("lang") === "en" ? "en" : "kr";
  var other = lang === "en" ? "kr" : "en";
  var file = (location.pathname.split("/").pop() || "00-flow.html").split("?")[0];
  var base = "/static/checklist-preview/";

  var copy =
    lang === "en"
      ? {
          flow: "Full flow",
          arrival: "Day 1 sample",
          money: "Money sample",
          ko: "한국어",
          en: "English",
          aria: "Preview navigation"
        }
      : {
          flow: "전체 플로",
          arrival: "1일 샘플",
          money: "돈 샘플",
          ko: "한국어",
          en: "English",
          aria: "미리보기 메뉴"
        };

  var pages = [
    { href: "00-flow.html", label: copy.flow, track: "flow" },
    { href: "02-day-01.html", label: copy.arrival, track: "arrival" },
    { href: "20-later-money.html", label: copy.money, track: "money" }
  ];

  function build() {
    var bar = document.createElement("nav");
    bar.className = "preview-bar no-print";
    bar.setAttribute("aria-label", copy.aria);

    var langs = document.createElement("div");
    langs.className = "preview-bar__langs";

    var aKo = document.createElement("a");
    aKo.href = base + "kr/" + file;
    aKo.textContent = copy.ko;
    aKo.setAttribute("data-track", "checklist_preview_lang");
    aKo.setAttribute("data-track-label", lang + "_to_kr");
    aKo.setAttribute("data-track-lang", "kr");
    if (lang === "kr") aKo.className = "is-current";
    aKo.setAttribute("hreflang", "ko");

    var aEn = document.createElement("a");
    aEn.href = base + "en/" + file;
    aEn.textContent = copy.en;
    aEn.setAttribute("data-track", "checklist_preview_lang");
    aEn.setAttribute("data-track-label", lang + "_to_en");
    aEn.setAttribute("data-track-lang", "en");
    if (lang === "en") aEn.className = "is-current";
    aEn.setAttribute("hreflang", "en");

    langs.appendChild(aKo);
    langs.appendChild(aEn);

    var pagesEl = document.createElement("div");
    pagesEl.className = "preview-bar__pages";
    pages.forEach(function (item) {
      var a = document.createElement("a");
      a.href = base + lang + "/" + item.href;
      a.textContent = item.label;
      a.setAttribute("data-track", "checklist_preview_nav");
      a.setAttribute("data-track-label", lang + "_" + item.track);
      a.setAttribute("data-track-lang", lang);
      if (item.href === file) a.className = "is-current";
      pagesEl.appendChild(a);
    });

    bar.appendChild(langs);
    bar.appendChild(pagesEl);
    document.body.insertBefore(bar, document.body.firstChild);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
