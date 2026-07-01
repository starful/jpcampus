/* Shared clipboard helper (share bar + compare page). */
(function (global) {
    async function copyText(text) {
        try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(text);
                return true;
            }
        } catch (_) { /* fallback below */ }
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        try {
            return document.execCommand("copy");
        } catch (_) {
            return false;
        } finally {
            document.body.removeChild(ta);
        }
    }

    global.JPCampusClipboard = { copyText };
})(typeof window !== "undefined" ? window : globalThis);
