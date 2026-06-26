(function () {
  const root = document.getElementById("admin-reports-page");
  if (!root) return;

  const flash = document.getElementById("admin-reports-flash");
  const form = document.getElementById("admin-reports-date-form");
  const dateInput = document.getElementById("admin-reports-start-from");
  const statusFilter = document.getElementById("admin-reports-status-filter");
  const listEl = document.getElementById("admin-reports-list");
  const emptyEl = document.getElementById("admin-reports-empty");
  const dataEl = document.getElementById("admin-reports-data");

  function showFlash(message, variant) {
    if (!flash) return;
    flash.textContent = message;
    flash.className = "alert " + (variant || "alert-danger");
    flash.classList.remove("d-none");
  }

  function hideFlash() {
    if (!flash) return;
    flash.classList.add("d-none");
  }

  function formatDt(iso) {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleString("ru-RU", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return String(iso);
    }
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  // Генерация ссылки на профиль пользователя
  function profileLink(user) {
    if (!user) return "—";
    if (user.username) {
      const url = `/user/${encodeURIComponent(user.username)}`;
      return `<a href="${url}" class="text-decoration-none">${escapeHtml(user.username)}</a>`;
    } else if (user.id) {
      const url = `/users/${encodeURIComponent(user.id)}`;
      return `<a href="${url}" class="text-decoration-none">${escapeHtml(String(user.id))}</a>`;
    }
    return "—";
  }

  function renderOneReport(r) {
    const card = document.createElement("article");
    card.className = "card";
    const solvedBadge = r.solved
      ? '<span class="badge bg-success">Решена</span>'
      : '<span class="badge bg-warning text-dark">Не решена</span>';
    const commentPart =
      r.comment && r.comment.id != null
        ? '<p class="small mb-1"><strong>Комментарий:</strong> ' +
          escapeHtml(String(r.comment.text)) +
          "</p>"
        : "";
    const solveBtn =
      r.solved
        ? ""
        : '<button type="button" class="btn btn-sm btn-outline-success js-solve-report" data-report-id="' +
          escapeHtml(String(r.id)) +
          '">Отметить как решённую</button>';

    card.innerHTML =
      '<div class="card-body">' +
      '<div class="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-2">' +
      '<div><h2 class="h6 mb-1">Жалоба #' +
      escapeHtml(String(r.id)) +
      "</h2>" +
      '<p class="small text-muted mb-0">' +
      formatDt(r.created_at) +
      "</p></div>" +
      solvedBadge +
      "</div>" +
      '<p class="small mb-1"><strong>Причина:</strong> ' +
      escapeHtml(r.reason || "Не указана") +
      "</p>" +
      '<p class="small mb-1"><strong>На пользователя:</strong> ' +
      profileLink(r.user) +
      "</p>" +
      '<p class="small mb-2"><strong>Создал:</strong> ' +
      profileLink(r.created_by) +
      "</p>" +
      commentPart +
      '<div class="mt-2">' +
      solveBtn +
      "</div>" +
      "</div>";
    return card;
  }

  function parseInitialData() {
    if (!dataEl) return [];
    try {
      return JSON.parse(dataEl.textContent || "[]");
    } catch {
      return [];
    }
  }

  let reports = parseInitialData();

  function getFiltered() {
    const mode = statusFilter ? statusFilter.value : "all";
    if (mode === "solved") return reports.filter(function (r) { return Boolean(r.solved); });
    if (mode === "open") return reports.filter(function (r) { return !r.solved; });
    return reports;
  }

  function renderList() {
    if (!listEl) return;
    const filtered = getFiltered();
    listEl.innerHTML = "";
    filtered.forEach(function (r) {
      listEl.appendChild(renderOneReport(r));
    });
    if (emptyEl) emptyEl.classList.toggle("d-none", filtered.length > 0);
  }

  async function loadReportsByDate() {
    hideFlash();
    const params = new URLSearchParams();
    if (dateInput && dateInput.value) params.set("start_from", dateInput.value);
    const url = "/admin/reports" + (params.toString() ? "?" + params.toString() : "");
    try {
      const res = await fetch(url, {
        method: "GET",
        credentials: "include",
        headers: { Accept: "application/json" },
      });
      if (!res.ok) {
        throw new Error("Не удалось загрузить жалобы");
      }
      reports = await res.json();
      renderList();
    } catch (err) {
      showFlash(err.message || "Ошибка загрузки", "alert-danger");
    }
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      loadReportsByDate();
    });
  }

  if (statusFilter) {
    statusFilter.addEventListener("change", renderList);
  }

  if (listEl) {
    listEl.addEventListener("click", async function (e) {
      const btn = e.target.closest(".js-solve-report");
      if (!btn) return;
      const reportId = btn.getAttribute("data-report-id");
      if (!reportId) return;
      hideFlash();
      try {
        const res = await fetch("/admin/reports/" + encodeURIComponent(reportId) + "/solve", {
          method: "PATCH",
          credentials: "include",
          headers: { Accept: "application/json" },
        });
        if (!res.ok) throw new Error("Не удалось обновить статус жалобы");
        const updated = await res.json();
        reports = reports.map(function (r) {
          return String(r.id) === String(updated.id) ? updated : r;
        });
        renderList();
      } catch (err) {
        showFlash(err.message || "Ошибка", "alert-danger");
      }
    });
  }

  renderList();
})();
