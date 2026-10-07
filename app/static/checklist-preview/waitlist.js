/* Email waitlist form → POST /api/checklist-waitlist (Firestore via reactions DB) */
(function () {
  var lang = document.documentElement.getAttribute("lang") === "en" ? "en" : "kr";
  var source =
    document.body.getAttribute("data-preview-page") ||
    (lang === "en" ? "en_preview" : "kr_preview");

  var copy =
    lang === "en"
      ? {
          title: "Get launch email",
          hint: "We’ll email you when the paid Korean checklist goes on sale. No spam.",
          placeholder: "you@example.com",
          submit: "Notify me",
          ok: "Saved. We’ll email you at launch.",
          exists: "You’re already on the list.",
          err: "Could not save. Try again.",
          invalid: "Enter a valid email."
        }
      : {
          title: "출시 알림 받기",
          hint: "유료 한국어 체크리스트가 나오면 이메일로 알려 드립니다. 스팸 없습니다.",
          placeholder: "you@example.com",
          submit: "알림 받기",
          ok: "저장했습니다. 출시 때 메일로 알려 드릴게요.",
          exists: "이미 등록된 이메일입니다.",
          err: "저장에 실패했습니다. 다시 시도해 주세요.",
          invalid: "올바른 이메일을 입력해 주세요."
        };

  function track(action, label) {
    if (typeof window.gtag !== "function") return;
    window.gtag("event", action, {
      event_category: "engagement",
      event_label: label,
      language: lang,
      transport_type: "beacon"
    });
  }

  function mount() {
    var nodes = document.querySelectorAll("[data-waitlist]");
    if (!nodes.length) return;

    nodes.forEach(function (el) {
      var src = el.getAttribute("data-waitlist-source") || source;
      el.innerHTML =
        '<form class="waitlist-form" novalidate>' +
        '<p class="waitlist-form__title">' +
        copy.title +
        "</p>" +
        '<p class="waitlist-form__hint">' +
        copy.hint +
        "</p>" +
        '<label class="waitlist-form__hp" aria-hidden="true">Company' +
        '<input type="text" name="website" tabindex="-1" autocomplete="off">' +
        "</label>" +
        '<div class="waitlist-form__row">' +
        '<input class="waitlist-form__email" type="email" name="email" required ' +
        'placeholder="' +
        copy.placeholder +
        '" autocomplete="email">' +
        '<button class="waitlist-form__btn" type="submit">' +
        copy.submit +
        "</button>" +
        "</div>" +
        '<p class="waitlist-form__msg" role="status" hidden></p>' +
        "</form>";

      var form = el.querySelector("form");
      var msg = el.querySelector(".waitlist-form__msg");
      var btn = el.querySelector(".waitlist-form__btn");

      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var email = (form.email.value || "").trim();
        var website = (form.website.value || "").trim();
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          msg.hidden = false;
          msg.textContent = copy.invalid;
          msg.className = "waitlist-form__msg is-err";
          return;
        }
        btn.disabled = true;
        fetch("/api/checklist-waitlist", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: email,
            lang: lang,
            source: src,
            website: website
          })
        })
          .then(function (res) {
            return res.json().then(function (data) {
              return { ok: res.ok, status: res.status, data: data };
            });
          })
          .then(function (result) {
            msg.hidden = false;
            if (!result.ok) {
              msg.className = "waitlist-form__msg is-err";
              msg.textContent = copy.err;
              track("waitlist_error", src);
              return;
            }
            msg.className = "waitlist-form__msg is-ok";
            var action = (result.data && result.data.action) || "created";
            msg.textContent = action === "exists" ? copy.exists : copy.ok;
            track("cta_checklist_interest", src);
            track("waitlist_submit", src + "_" + action);
            form.email.value = "";
          })
          .catch(function () {
            msg.hidden = false;
            msg.className = "waitlist-form__msg is-err";
            msg.textContent = copy.err;
            track("waitlist_error", src);
          })
          .finally(function () {
            btn.disabled = false;
          });
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
