(function () {
    function trackShare(method, shareId) {
        if (typeof gtag !== "function") return;
        gtag("event", "share", {
            method: method,
            content_type: "article",
            item_id: shareId || "",
        });
    }

    function flashButton(btn, label) {
        var original = btn.textContent;
        btn.textContent = label;
        btn.disabled = true;
        window.setTimeout(function () {
            btn.textContent = original;
            btn.disabled = false;
        }, 1800);
    }

    document.querySelectorAll(".share-bar").forEach(function (bar) {
        var shareId = bar.dataset.shareId || "";
        var shareUrl = bar.dataset.shareUrl || "";
        var shareText = bar.dataset.shareText || "";
        var copyLabel = bar.dataset.copyLabel || "Copied!";

        var nativeBtn = bar.querySelector('[data-share-method="native"]');
        if (nativeBtn && navigator.share) {
            nativeBtn.hidden = false;
        }

        bar.querySelectorAll("[data-share-method]").forEach(function (el) {
            el.addEventListener("click", function (event) {
                var method = el.dataset.shareMethod;
                if (method === "twitter" || method === "linkedin") {
                    trackShare(method, shareId);
                    return;
                }
                if (method === "native") {
                    event.preventDefault();
                    if (!navigator.share) return;
                    navigator.share({
                        title: document.title,
                        text: shareText,
                        url: shareUrl,
                    }).then(function () {
                        trackShare("native", shareId);
                    }).catch(function () {});
                    return;
                }
                if (method === "copy_link") {
                    event.preventDefault();
                    JPCampusClipboard.copyText(shareUrl).then(function (ok) {
                        if (!ok) return;
                        flashButton(el, copyLabel);
                        trackShare("copy_link", shareId);
                    });
                }
            });
        });
    });
})();
