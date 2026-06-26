/**
 * Страница персоны: нормализация URL медиа, обновление из API.
 */
(function () {
  function normalizeMediaUrl(url) {
    if (!url || typeof url !== "string") return url;
    var u = url.trim();
    while (u.indexOf("https:https://") !== -1) {
      u = u.replace("https:https://", "https://");
    }
    while (u.indexOf("http:https://") !== -1) {
      u = u.replace("http:https://", "https://");
    }
    while (u.indexOf("https:http://") !== -1) {
      u = u.replace("https:http://", "http://");
    }
    return u;
  }

  function fixImgSrc(img) {
    if (!img || !img.getAttribute) return;
    var src = img.getAttribute("src");
    if (!src) return;
    var fixed = normalizeMediaUrl(src);
    if (fixed !== src) img.setAttribute("src", fixed);
  }

  document.querySelectorAll(".person-page img[src]").forEach(fixImgSrc);

  var root = document.getElementById("person-page");
  if (!root) return;

  var personId = root.getAttribute("data-person-id");
  var btn = document.getElementById("person-page-refresh-btn");
  if (!btn || !personId) return;

  btn.addEventListener("click", function () {
    btn.disabled = true;
    fetch("/person/" + encodeURIComponent(personId) + "/refresh", {
      method: "POST",
      credentials: "include",
      headers: { Accept: "application/json" },
    })
      .then(function (res) {
        if (res.status === 401) {
          window.location.href = "/login";
          return;
        }
        if (!res.ok) {
          return res.json().then(function (d) {
            var msg =
              typeof d.detail === "string"
                ? d.detail
                : Array.isArray(d.detail)
                  ? (d.detail[0] && d.detail[0].msg) || JSON.stringify(d.detail)
                  : "Ошибка обновления";
            throw new Error(msg);
          });
        }
        window.location.reload();
      })
      .catch(function (e) {
        window.alert(e.message || "Не удалось обновить данные");
      })
      .finally(function () {
        btn.disabled = false;
      });
  });
})();
