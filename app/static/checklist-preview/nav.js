/* Preview-only TOC: flow · arrival · money */
(function () {
  var lang = document.documentElement.getAttribute("lang") === "en" ? "en" : "kr";
  var base = "/static/checklist-preview/" + lang + "/";
  var labels =
    lang === "en"
      ? [
          { href: "00-flow.html", label: "Full flow", track: "flow" },
          { href: "02-day-01.html", label: "Day 1 arrival", track: "arrival" },
          { href: "20-later-money.html", label: "Later · money", track: "money" }
        ]
      : [
          { href: "00-flow.html", label: "전체 플로", track: "flow" },
          { href: "02-day-01.html", label: "1일 도착", track: "arrival" },
          { href: "20-later-money.html", label: "이후 · 돈", track: "money" }
        ];

  var file = (location.pathname.split("/").pop() || "").split("?")[0];

  function build() {
    document.body.classList.add("has-side-nav");
    var aside = document.createElement("aside");
    aside.className = "side-nav no-print";
    aside.setAttribute("aria-label", lang === "en" ? "Preview pages" : "미리보기 목차");

    var brand = document.createElement("p");
    brand.className = "side-nav__brand";
    brand.textContent = lang === "en" ? "Preview" : "미리보기";
    aside.appendChild(brand);

    var list = document.createElement("ul");
    list.className = "side-nav__list";
    labels.forEach(function (item) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = base + item.href;
      a.textContent = item.label;
      a.setAttribute("data-track", "checklist_preview_nav");
      a.setAttribute("data-track-label", lang + "_" + item.track);
      a.setAttribute("data-track-lang", lang);
      if (item.href === file) {
        a.className = "is-current";
        a.setAttribute("aria-current", "page");
      }
      li.appendChild(a);
      list.appendChild(li);
    });
    aside.appendChild(list);

    var fab = document.createElement("button");
    fab.type = "button";
    fab.className = "side-nav__fab no-print";
    fab.setAttribute("aria-label", lang === "en" ? "Open menu" : "목차 열기");
    fab.textContent = lang === "en" ? "Menu" : "목차";
    fab.addEventListener("click", function () {
      var open = aside.classList.toggle("is-open");
      fab.setAttribute("aria-expanded", open ? "true" : "false");
      fab.textContent = open
        ? lang === "en"
          ? "Close"
          : "닫기"
        : lang === "en"
          ? "Menu"
          : "목차";
    });

    document.body.appendChild(aside);
    document.body.appendChild(fab);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
