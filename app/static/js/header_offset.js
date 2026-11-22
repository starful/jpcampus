/* app/static/js/header_offset.js — keeps --header-h in sync with the sticky
   header's real height so the mobile quick-action CTA can stick right below it. */
(function () {
    var header = document.querySelector(".site-header");
    if (!header) return;

    function setHeaderHeight() {
        document.documentElement.style.setProperty("--header-h", header.offsetHeight + "px");
    }

    setHeaderHeight();
    window.addEventListener("resize", setHeaderHeight);

    if (typeof ResizeObserver !== "undefined") {
        new ResizeObserver(setHeaderHeight).observe(header);
    }
})();
