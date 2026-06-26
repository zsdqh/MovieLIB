/**
 * Главная / и /search: пагинация через JSON (режим home или search).
 */
(function () {
  const ACCEPT_JSON = "application/json";

  const MOVIE_TYPE_LABELS = {
    1: "Фильм",
    2: "Сериал",
    3: "Мультфильм",
    4: "Аниме",
    5: "Мультсериал",
    6: "Ремейк",
  };

  function movieTypeLabel(type) {
    if (type == null) return "";
    const n = typeof type === "number" ? type : parseInt(String(type), 10);
    return MOVIE_TYPE_LABELS[n] || String(type);
  }

  function mergeHeaders(extra) {
    const h = new Headers(extra || {});
    if (!h.has("Accept")) h.set("Accept", ACCEPT_JSON);
    return h;
  }

  async function parseError(response) {
    try {
      const data = await response.json();
      return data.detail || data.message || response.statusText;
    } catch {
      return response.statusText || "Ошибка запроса";
    }
  }

  async function apiFetch(url, options) {
    const opts = Object.assign({ credentials: "include" }, options);
    opts.headers = mergeHeaders(opts.headers);
    const res = await fetch(url, opts);
    if (res.status === 401) {
      window.location.href = "/login";
      throw new Error("Требуется вход");
    }
    if (!res.ok) {
      const msg = await parseError(res);
      throw new Error(msg);
    }
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("application/json")) {
      const text = await res.text();
      return text ? JSON.parse(text) : null;
    }
    return null;
  }

  function showFlash(el, message, variant) {
    if (!el) return;
    el.textContent = message;
    el.className = "alert " + (variant || "alert-danger");
    el.classList.remove("d-none");
  }

  function hideFlash(el) {
    if (!el) return;
    el.classList.add("d-none");
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function escapeAttr(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;");
  }

  function renderGenreBadges(genres) {
    if (!genres || !genres.length) return "";
    return genres
      .map(function (g) {
        const label = typeof g === "string" ? g : g && g.name != null ? String(g.name) : String(g);
        return (
          '<span class="badge bg-secondary bg-opacity-25 text-dark fw-normal">' + escapeHtml(label) + "</span>"
        );
      })
      .join("");
  }

  function renderMovieCard(movie) {
    const poster = movie.poster
      ? '<img src="' +
        escapeAttr(movie.poster) +
        '" alt="" class="movie-card-poster img-fluid" loading="lazy" />'
      : '<div class="movie-card-poster-placeholder">Нет постера</div>';
    const typeLabel = movieTypeLabel(movie.type);
    const genresHtml = renderGenreBadges(movie.genres);
    return (
      '<div class="movies-grid-item">' +
      '<article class="card movie-card h-100 shadow-sm">' +
      '<a href="/movie/' +
      encodeURIComponent(String(movie.id)) +
      '/" class="movie-card-link stretched-link text-decoration-none text-reset">' +
      '<div class="movie-card-inner text-center">' +
      '<div class="movie-card-poster-wrap mx-auto">' +
      poster +
      "</div>" +
      '<div class="card-body d-flex flex-column align-items-center py-3">' +
      '<h2 class="h6 card-title movie-card-title mb-2">' +
      escapeHtml(movie.name) +
      "</h2>" +
      '<p class="small text-muted mb-2 movie-card-type">' +
      escapeHtml(typeLabel) +
      "</p>" +
      '<div class="movie-card-genres small justify-content-center">' +
      genresHtml +
      "</div>" +
      "</div></div></a></article></div>"
    );
  }

  function renderGrid(gridEl, movies) {
    if (!gridEl) return;
    gridEl.innerHTML = (movies || []).map(renderMovieCard).join("");
  }

  function setEmptyVisible(emptyEl, visible) {
    if (!emptyEl) return;
    emptyEl.classList.toggle("d-none", !visible);
  }

  function syncPagination(root, page, hasMovies) {
    const prev = root.querySelector("#movies-prev");
    const next = root.querySelector("#movies-next");
    const label = root.querySelector("#movies-page-label");
    if (label) label.textContent = "Страница " + page;
    if (prev) prev.disabled = page <= 1;
    if (next) next.disabled = !hasMovies;
  }

  const root = document.getElementById("movies-results-page");
  if (!root) return;

  const kind = root.dataset.pageKind;
  if (kind !== "home" && kind !== "search") return;

  const grid = document.getElementById("movies-grid");
  const emptyEl = document.getElementById("movies-empty");
  const flash = document.getElementById("movies-flash");
  const searchInput = document.getElementById("movies-search-input");
  const prevBtn = document.getElementById("movies-prev");
  const nextBtn = document.getElementById("movies-next");

  let page = parseInt(root.dataset.page || "1", 10) || 1;
  let query = root.dataset.query || "";

  function applyState(data) {
    const movies = data && data.movies ? data.movies : [];
    page = data && data.page != null ? parseInt(String(data.page), 10) || 1 : page;
    if (data && data.query != null) query = String(data.query);
    root.dataset.page = String(page);
    root.dataset.query = query;
    if (searchInput && data && data.query != null) searchInput.value = query;
    renderGrid(grid, movies);
    setEmptyVisible(emptyEl, movies.length === 0);
    syncPagination(root, page, movies.length > 0);
    window.scrollTo({ top: 0, behavior: 'smooth' });

  }

  function buildPageUrl(nextPage) {
    if (kind === "home") {
      return "/?page=" + encodeURIComponent(String(nextPage));
    }
    const q = (query || "").trim();
    if (!q) return null;
    return (
      "/search?query=" +
      encodeURIComponent(q) +
      "&page=" +
      encodeURIComponent(String(nextPage))
    );
  }

  async function loadPage(direction) {
    hideFlash(flash);
    const nextPage = page + (direction === "next" ? 1 : -1);
    if (nextPage < 1) return;
    const url = buildPageUrl(nextPage);
    if (!url) {
      showFlash(flash, "Введите запрос для перехода по страницам поиска.", "alert-warning");
      return;
    }
    try {
      const data = await apiFetch(url, { method: "GET" });
      if (!data || !data.movies || data.movies.length === 0) {
        if (direction === "next") {
          showFlash(flash, "Это последняя страница.", "alert-info");
          window.scrollTo({ top: 0, behavior: 'smooth' });
          return;
        }
        showFlash(flash, "Нет результатов на этой странице.", "alert-warning");
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }
      applyState(data);
    } catch (e) {
      showFlash(flash, e.message || "Не удалось загрузить страницу");
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  if (prevBtn) {
    prevBtn.addEventListener("click", function () {
      if (page <= 1) return;
      loadPage("prev");
    window.scrollTo({ top: 0, behavior: 'smooth' });

    });
  }
  if (nextBtn) {
    nextBtn.addEventListener("click", function () {
      loadPage("next");
    window.scrollTo({ top: 0, behavior: 'smooth' });

    });
  }
})();
