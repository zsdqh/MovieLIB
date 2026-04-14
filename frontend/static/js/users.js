/**
 * Профиль: вкладки, списки (слева карточки фильмов, справа навигация по спискам), комментарии.
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
    if (res.status === 204) return null;
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
    el.className = "alert " + (variant || "alert-info");
    el.classList.remove("d-none");
  }

  function hideFlash(el) {
    if (!el) return;
    el.classList.add("d-none");
  }

  function formatDt(iso) {
    if (!iso) return "";
    try {
      const d = new Date(iso);
      return d.toLocaleString("ru-RU", {
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

  function escapeAttr(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;");
  }

  function formatCommentRating(rating) {
    const raw = Number(rating);
    const n = Number.isFinite(raw) ? raw : 0;
    if (n < 0) {
      return (
        '<span class="user-comment-rating user-comment-rating--neg" title="Рейтинг">−' +
        Math.abs(n) +
        "</span>"
      );
    }
    if (n > 0) {
      return (
        '<span class="user-comment-rating user-comment-rating--pos" title="Рейтинг">+' +
        n +
        "</span>"
      );
    }
    return '<span class="user-comment-rating user-comment-rating--zero" title="Рейтинг">0</span>';
  }

  function renderComment(c) {
    const art = document.createElement("article");
    art.className = "comment-card card mb-2";
    const movieLink =
      c.movie_id != null
        ? '<a href="/movie/' +
          c.movie_id +
          '/">фильм #' +
          c.movie_id +
          "</a>"
        : "";
    const ratingHtml = formatCommentRating(c.rating);
    art.innerHTML =
      '<div class="card-body py-2 px-3">' +
      '<p class="mb-1">' +
      escapeHtml(c.text) +
      "</p>" +
      '<p class="comment-meta mb-0 d-flex flex-wrap align-items-center gap-2">' +
      '<span class="comment-meta-rating">' +
      ratingHtml +
      "</span>" +
      '<span class="comment-meta-rest">' +
      formatDt(c.created_at) +
      (movieLink ? " · " + movieLink : "") +
      "</span>" +
      "</p>" +
      "</div>";
    return art;
  }

  function mergeAllMovies(lists) {
    const map = new Map();
    (lists || []).forEach(function (lst) {
      (lst.movies || []).forEach(function (m) {
        if (!map.has(m.id)) map.set(m.id, m);
      });
    });
    return Array.from(map.values());
  }

  function renderMovieCard(m, opts) {
    opts = opts || {};
    const showRemove = Boolean(opts.showRemove && opts.listId != null);
    const compareStatus = opts.compareStatus || "";
    const col = document.createElement("div");
    col.className = "col-6 col-sm-4 col-md-4 col-lg-3";
    const poster = m.poster || "";
    const name = m.name || "";
    const typeLabel = movieTypeLabel(m.type);
    const compareClass =
      compareStatus === "hit"
        ? " profile-movie-card-compare-hit"
        : compareStatus === "miss"
          ? " profile-movie-card-compare-miss"
          : "";
    const removeBtn =
      showRemove ?
        '<button type="button" class="btn btn-sm btn-outline-danger profile-movie-remove" title="Удалить из списка" data-list-id="' +
        escapeAttr(String(opts.listId)) +
        '" data-movie-id="' +
        escapeAttr(String(m.id)) +
        '"><i class="fa-solid fa-xmark" aria-hidden="true"></i></button>'
      : "";
    col.innerHTML =
      '<div class="position-relative profile-movie-card-wrap h-100' +
      compareClass +
      '">' +
      removeBtn +
      '<a href="/movie/' +
      m.id +
      '/" class="movie-card-tile text-decoration-none text-dark d-block h-100">' +
      '<div class="movie-card-poster-wrap">' +
      '<img src="' +
      escapeAttr(poster) +
      '" alt="" class="movie-card-poster" loading="lazy" />' +
      "</div>" +
      '<div class="small fw-semibold mt-2">' +
      escapeHtml(name) +
      "</div>" +
      '<div class="small text-muted">' +
      escapeHtml(typeLabel) +
      "</div>" +
      "</a></div>";
    return col;
  }

  function parseListsData() {
    const el = document.getElementById("profile-lists-data");
    if (!el) return [];
    try {
      return JSON.parse(el.textContent);
    } catch {
      return [];
    }
  }

  function listVisibilityBadgeHtml(isPublic) {
    if (isPublic) {
      return '<span class="badge rounded-pill bg-secondary list-nav-visibility">Публичный</span>';
    }
    return '<span class="badge rounded-pill bg-light text-dark border list-nav-visibility">Приватный</span>';
  }

  function initProfileLists() {
    const page = document.querySelector(".users-page[data-user-id]");
    if (!page) return;

    const mode = page.getAttribute("data-profile-mode") || "view";
    const isMe = mode === "me";
    const lists = parseListsData();
    const nav = document.getElementById("profile-list-nav");
    const grid = document.getElementById("profile-movies-grid");
    const empty = document.getElementById("profile-movies-empty");
    const flash = document.getElementById("users-flash");

    if (!nav || !grid || !empty) return;

    const merged = mergeAllMovies(lists);
    let allBtn = null;
    let allCountEl = null;
    let meProfileLists = null;
    let compareMovieIdsByListId = null;
    let compareActiveForListId = null;

    let selectedKey = "all";
    const byId = {};
    lists.forEach(function (lst) {
      byId[String(lst.id)] = lst;
    });

    function setActiveNav(key) {
      selectedKey = key;
      nav.querySelectorAll(".list-nav-row").forEach(function (el) {
        el.classList.remove("active");
      });
      if (allBtn) allBtn.classList.remove("active");
      if (key === "all") {
        if (allBtn) allBtn.classList.add("active");
      } else {
        const row = nav.querySelector('.list-nav-row[data-list-key="' + key + '"]');
        if (row) row.classList.add("active");
      }
    }

    function showMovies(movies) {
      grid.innerHTML = "";
      if (!movies || movies.length === 0) {
        empty.classList.remove("d-none");
        return;
      }
      empty.classList.add("d-none");
      const listIdForRemove = isMe && selectedKey !== "all" ? selectedKey : null;
      const compareSet =
        !isMe &&
        selectedKey !== "all" &&
        compareActiveForListId != null &&
        String(compareActiveForListId) === String(selectedKey) &&
        compareMovieIdsByListId &&
        compareMovieIdsByListId[String(selectedKey)] instanceof Set
          ? compareMovieIdsByListId[String(selectedKey)]
          : null;
      movies.forEach(function (m) {
        let compareStatus = "";
        if (compareSet) {
          compareStatus = compareSet.has(String(m.id)) ? "hit" : "miss";
        }
        grid.appendChild(
          renderMovieCard(m, {
            showRemove: Boolean(listIdForRemove),
            listId: listIdForRemove,
            compareStatus: compareStatus,
          })
        );
      });
    }

    function applySelection() {
      if (selectedKey === "all") {
        showMovies(mergeAllMovies(lists));
        return;
      }
      const lst = byId[selectedKey];
      showMovies(lst && lst.movies ? lst.movies : []);
    }

    nav.innerHTML = "";
    lists.forEach(function (lst) {
      const count = (lst.movies || []).length;
      const idStr = String(lst.id);
      const pub = Boolean(lst.is_public);
      if (isMe) {
        const wrap = document.createElement("div");
        wrap.className = "list-group-item list-nav-row py-2";
        wrap.setAttribute("data-list-key", idStr);

        const head = document.createElement("div");
        head.className = "list-nav-item-head";

        const headRow = document.createElement("div");
        headRow.className =
          "d-flex justify-content-between align-items-start gap-2";

        const sel = document.createElement("button");
        sel.type = "button";
        sel.className =
          "btn btn-link text-start p-0 flex-grow-1 list-nav-select text-decoration-none";
        sel.setAttribute("data-list-key", idStr);
        sel.innerHTML =
          '<div class="list-nav-btn-inner">' +
          '<div class="fw-semibold text-body">' +
          escapeHtml(lst.name) +
          "</div>" +
          '<div class="d-flex flex-wrap align-items-center gap-1 mt-1">' +
          '<span class="text-muted small">(' +
          count +
          ")</span>" +
          listVisibilityBadgeHtml(pub) +
          "</div></div>";

        const tools = document.createElement("div");
        tools.className = "btn-group btn-group-sm flex-shrink-0";
        tools.innerHTML =
          '<button type="button" class="btn btn-outline-secondary btn-edit-list" title="Изменить название и доступность" data-list-id="' +
          idStr +
          '">✎</button>' +
          '<button type="button" class="btn btn-outline-danger btn-delete-list" title="Удалить" data-list-id="' +
          idStr +
          '">×</button>';

        headRow.appendChild(sel);
        headRow.appendChild(tools);
        head.appendChild(headRow);

        const edit = document.createElement("div");
        edit.className = "list-nav-edit d-none border-top pt-2 mt-2";

        const lblName = document.createElement("label");
        lblName.className = "form-label small mb-1";
        lblName.textContent = "Название";
        const inpName = document.createElement("input");
        inpName.type = "text";
        inpName.className = "form-control form-control-sm list-name-input";
        inpName.value = lst.name || "";

        const chkWrap = document.createElement("div");
        chkWrap.className = "form-check mt-2";
        const chk = document.createElement("input");
        chk.type = "checkbox";
        chk.className = "form-check-input list-public-input";
        chk.id = "list-pub-" + idStr;
        chk.checked = pub;
        const lblChk = document.createElement("label");
        lblChk.className = "form-check-label small";
        lblChk.setAttribute("for", chk.id);
        lblChk.textContent = "Публичный список (виден другим)";
        chkWrap.appendChild(chk);
        chkWrap.appendChild(lblChk);

        const editBtns = document.createElement("div");
        editBtns.className = "mt-2 d-flex flex-wrap gap-1";
        const btnSave = document.createElement("button");
        btnSave.type = "button";
        btnSave.className = "btn btn-sm btn-primary btn-save-list";
        btnSave.setAttribute("data-list-id", idStr);
        btnSave.textContent = "Сохранить";
        const btnCancel = document.createElement("button");
        btnCancel.type = "button";
        btnCancel.className = "btn btn-sm btn-outline-secondary btn-cancel-edit";
        btnCancel.textContent = "Отмена";
        editBtns.appendChild(btnSave);
        editBtns.appendChild(btnCancel);

        edit.appendChild(lblName);
        edit.appendChild(inpName);
        edit.appendChild(chkWrap);
        edit.appendChild(editBtns);

        wrap.appendChild(head);
        wrap.appendChild(edit);
        nav.appendChild(wrap);
      } else {
        const row = document.createElement("div");
        row.className = "list-group-item list-nav-row py-2";
        row.setAttribute("data-list-key", idStr);
        const rowTop = document.createElement("div");
        rowTop.className = "d-flex justify-content-between align-items-start gap-2";
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className =
          "btn btn-link text-start p-0 flex-grow-1 list-nav-select text-decoration-none";
        btn.setAttribute("data-list-key", idStr);
        btn.innerHTML =
          '<div class="list-nav-btn-inner">' +
          '<div class="fw-semibold text-body">' +
          escapeHtml(lst.name) +
          "</div>" +
          '<div class="d-flex flex-wrap align-items-center gap-1 mt-1">' +
          '<span class="text-muted small">(' +
          count +
          ")</span>" +
          listVisibilityBadgeHtml(pub) +
          "</div></div>";
        const compareBtn = document.createElement("button");
        compareBtn.type = "button";
        compareBtn.className = "btn btn-outline-success btn-sm profile-compare-list-btn";
        compareBtn.setAttribute("data-list-id", idStr);
        compareBtn.textContent = "Сравнить";
        rowTop.appendChild(btn);
        rowTop.appendChild(compareBtn);
        row.appendChild(rowTop);
        nav.appendChild(row);
      }
    });

    allBtn = document.createElement("button");
    allBtn.type = "button";
    allBtn.className =
      "list-group-item list-group-item-action list-nav-all list-nav-all-btn fw-semibold";
    allBtn.setAttribute("data-list-key", "all");
    allCountEl = document.createElement("span");
    allCountEl.className = "text-muted small";
    allCountEl.id = "profile-all-count";
    allCountEl.textContent = "(" + merged.length + ")";
    allBtn.appendChild(document.createTextNode("Все "));
    allBtn.appendChild(allCountEl);
    nav.appendChild(allBtn);

    grid.addEventListener("click", function (e) {
      const rm = e.target.closest(".profile-movie-remove");
      if (!rm) return;
      e.preventDefault();
      e.stopPropagation();
      const listId = rm.getAttribute("data-list-id");
      const mid = rm.getAttribute("data-movie-id");
      if (!listId || !mid) return;
      if (!window.confirm("Убрать этот фильм из списка?")) return;
      apiFetch("/list/" + encodeURIComponent(listId) + "/movies", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ movie_id: parseInt(mid, 10) }),
      })
        .then(function (updated) {
          if (updated && updated.id != null) {
            const idStr = String(updated.id);
            if (byId[idStr]) byId[idStr] = updated;
            const li = lists.findIndex(function (x) {
              return String(x.id) === idStr;
            });
            if (li >= 0) lists[li] = updated;
          }
          applySelection();
          if (allCountEl) {
            allCountEl.textContent = "(" + mergeAllMovies(lists).length + ")";
          }
        })
        .catch(function (err) {
          if (flash) showFlash(flash, err.message, "alert-danger");
        });
    });

    nav.addEventListener("click", function (e) {
      const del = e.target.closest(".btn-delete-list");
      if (del) {
        e.preventDefault();
        const id = del.getAttribute("data-list-id");
        if (!id || !window.confirm("Удалить этот список?")) return;
        apiFetch("/list/" + encodeURIComponent(id), { method: "DELETE" })
          .then(function () {
            window.location.reload();
          })
          .catch(function (err) {
            if (flash) showFlash(flash, err.message, "alert-danger");
          });
        return;
      }

      const save = e.target.closest(".btn-save-list");
      if (save) {
        e.preventDefault();
        const id = save.getAttribute("data-list-id");
        const wrap = save.closest(".list-nav-row");
        if (!id || !wrap) return;
        const nameInp = wrap.querySelector(".list-name-input");
        const pubInp = wrap.querySelector(".list-public-input");
        const name = nameInp && nameInp.value.trim();
        const isPublic = pubInp && pubInp.checked;
        if (!name) {
          if (flash) showFlash(flash, "Укажите название списка", "alert-warning");
          return;
        }
        hideFlash(flash);
        apiFetch("/list/" + encodeURIComponent(id), {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: name, is_public: isPublic }),
        })
          .then(function () {
            window.location.reload();
          })
          .catch(function (err) {
            if (flash) showFlash(flash, err.message, "alert-danger");
          });
        return;
      }

      const cancel = e.target.closest(".btn-cancel-edit");
      if (cancel) {
        e.preventDefault();
        const wrap = cancel.closest(".list-nav-row");
        if (!wrap) return;
        const head = wrap.querySelector(".list-nav-item-head");
        const edit = wrap.querySelector(".list-nav-edit");
        const id = wrap.getAttribute("data-list-key");
        const lst = id ? byId[id] : null;
        if (head) head.classList.remove("d-none");
        if (edit) edit.classList.add("d-none");
        if (lst) {
          const ni = wrap.querySelector(".list-name-input");
          const pi = wrap.querySelector(".list-public-input");
          if (ni) ni.value = lst.name;
          if (pi) pi.checked = Boolean(lst.is_public);
        }
        return;
      }

      const ed = e.target.closest(".btn-edit-list");
      if (ed) {
        e.preventDefault();
        const wrap = ed.closest(".list-nav-row");
        if (!wrap) return;
        const head = wrap.querySelector(".list-nav-item-head");
        const edit = wrap.querySelector(".list-nav-edit");
        const id = ed.getAttribute("data-list-id");
        const lst = id ? byId[id] : null;
        if (!lst || !head || !edit) return;
        const ni = wrap.querySelector(".list-name-input");
        const pi = wrap.querySelector(".list-public-input");
        if (ni) ni.value = lst.name;
        if (pi) pi.checked = Boolean(lst.is_public);
        head.classList.add("d-none");
        edit.classList.remove("d-none");
        return;
      }

      if (e.target.closest(".list-nav-all")) {
        setActiveNav("all");
        applySelection();
        return;
      }

      if (e.target.closest(".list-nav-edit")) return;

      if (isMe) {
        const sel = e.target.closest(".list-nav-select");
        if (sel) {
          const wrap = sel.closest(".list-nav-row");
          const key = wrap && wrap.getAttribute("data-list-key");
          if (key) {
            setActiveNav(key);
            applySelection();
          }
        }
        return;
      }

      const compareBtn = e.target.closest(".profile-compare-list-btn");
      if (compareBtn) {
        e.preventDefault();
        const key = compareBtn.getAttribute("data-list-id");
        if (!key || !byId[key]) return;
        hideFlash(flash);
        const listName = String(byId[key].name || "").trim();
        if (!listName) {
          showFlash(flash, "Не удалось определить имя списка для сравнения", "alert-warning");
          return;
        }

        const normalizeListName = function (name) {
          return String(name || "").trim().toLowerCase();
        };

        const buildCompareIndex = function () {
          const myByName = new Map();
          (meProfileLists || []).forEach(function (lst) {
            const normalized = normalizeListName(lst && lst.name);
            if (!normalized || myByName.has(normalized)) return;
            const ids = new Set();
            (lst.movies || []).forEach(function (m) {
              if (m && m.id != null) ids.add(String(m.id));
            });
            myByName.set(normalized, ids);
          });

          const compareMap = {};
          lists.forEach(function (otherList) {
            const normalized = normalizeListName(otherList && otherList.name);
            compareMap[String(otherList.id)] = myByName.get(normalized) || new Set();
          });
          compareMovieIdsByListId = compareMap;
        };

        const applyCompare = function () {
          if (!compareMovieIdsByListId) buildCompareIndex();
          compareActiveForListId = key;
          setActiveNav(key);
          applySelection();
          showFlash(
            flash,
            'Сравнение со списком "' + listName + '" выполнено: зелёный — есть, красный — нет.',
            "alert-info"
          );
        };

        if (Array.isArray(meProfileLists)) {
          applyCompare();
          return;
        }

        apiFetch("/me?format=json", { method: "GET" })
          .then(function (meData) {
            meProfileLists =
              meData && Array.isArray(meData.user_lists) ? meData.user_lists : [];
            buildCompareIndex();
            applyCompare();
          })
          .catch(function (err) {
            showFlash(flash, err.message || "Не удалось получить ваши списки", "alert-danger");
          });
        return;
      }

      const viewSel = e.target.closest(".list-nav-select");
      if (viewSel) {
        const wrap = viewSel.closest(".list-nav-row");
        const key = wrap && wrap.getAttribute("data-list-key");
        if (key) {
          compareActiveForListId = null;
          setActiveNav(key);
          applySelection();
        }
      }
    });

    setActiveNav("all");
    applySelection();
  }

  let commentsStarted = false;
  let commentsNextPage = 0;
  let commentsLoading = false;
  let statsStarted = false;

  function startCommentsPagination() {
    const root = document.querySelector(".users-page[data-user-id]");
    if (!root) return;

    const userId = root.getAttribute("data-user-id");
    const container = document.getElementById("user-comments-root");
    const moreBtn = document.getElementById("user-comments-more");
    const emptyEl = document.getElementById("user-comments-empty");
    if (!userId || !container) return;

    async function loadPage() {
      if (commentsLoading) return;
      commentsLoading = true;
      if (moreBtn) moreBtn.disabled = true;
      try {
        const url =
          "/user/" +
          encodeURIComponent(userId) +
          "/comments?page=" +
          commentsNextPage;
        const data = await apiFetch(url, { method: "GET" });
        const comments = (data && data.comments) || [];
        if (commentsNextPage === 0 && comments.length === 0) {
          if (emptyEl) emptyEl.hidden = false;
        } else if (emptyEl) {
          emptyEl.hidden = true;
        }
        comments.forEach(function (c) {
          container.appendChild(renderComment(c));
        });
        commentsNextPage += 1;
        if (moreBtn) {
          moreBtn.hidden = !data.have_next;
        }
      } catch (e) {
        if (emptyEl) {
          emptyEl.textContent = e.message || "Не удалось загрузить комментарии";
          emptyEl.hidden = false;
        }
      } finally {
        commentsLoading = false;
        if (moreBtn) moreBtn.disabled = false;
      }
    }

    loadPage();
    if (moreBtn) {
      moreBtn.addEventListener("click", loadPage);
    }
  }

  function buildBars(container, items, maxVal) {
    if (!container) return;
    container.innerHTML = "";
    (items || []).forEach(function (item) {
      const row = document.createElement("div");
      row.className = "stats-bar-row";
      const pct = maxVal > 0 ? Math.max(2, Math.round((item.value / maxVal) * 100)) : 0;
      row.innerHTML =
        '<div class="stats-bar-label">' +
        escapeHtml(item.label) +
        '</div><div class="stats-bar-track"><div class="stats-bar-fill" style="width:' +
        pct +
        '%"></div></div><div class="stats-bar-value">' +
        escapeHtml(String(item.value)) +
        "</div>";
      container.appendChild(row);
    });
  }

  function renderTypesPie(container, legend, items) {
    if (!container || !legend) return;
    container.style.background = "";
    legend.innerHTML = "";
    const total = items.reduce(function (acc, x) {
      return acc + x.value;
    }, 0);
    if (total <= 0) return;

    const colors = ["#0d6efd", "#198754", "#dc3545", "#fd7e14", "#6f42c1", "#20c997"];
    let from = 0;
    const segments = [];
    items.forEach(function (it, idx) {
      const span = (it.value / total) * 100;
      const to = from + span;
      const color = colors[idx % colors.length];
      segments.push(color + " " + from.toFixed(2) + "% " + to.toFixed(2) + "%");
      from = to;

      const percent = ((it.value / total) * 100).toFixed(1);
      const row = document.createElement("div");
      row.className = "stats-legend-item";
      row.innerHTML =
        '<span class="stats-legend-color" style="background:' +
        color +
        '"></span><span class="stats-legend-label">' +
        escapeHtml(it.label) +
        '</span><span class="stats-legend-value">' +
        escapeHtml(String(it.value)) +
        " (" +
        escapeHtml(percent) +
        "%)</span>";
      legend.appendChild(row);
    });
    container.style.background = "conic-gradient(" + segments.join(", ") + ")";
  }

  function toYmd(dateObj) {
    if (!(dateObj instanceof Date) || Number.isNaN(dateObj.getTime())) return "";
    const y = dateObj.getFullYear();
    const m = String(dateObj.getMonth() + 1).padStart(2, "0");
    const d = String(dateObj.getDate()).padStart(2, "0");
    return y + "-" + m + "-" + d;
  }

  function parseIsoDate(value) {
    if (!value) return null;
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return null;
    return d;
  }

  function renderDailyColumns(container, rows) {
    if (!container) return;
    container.innerHTML = "";
    const maxVal = rows.reduce(function (acc, x) {
      return Math.max(acc, x.value);
    }, 0);
    rows.forEach(function (item) {
      if (item.value==0){
        return;
      }
      const col = document.createElement("div");
      col.className = "stats-daily-col";
      const height = maxVal > 0 ? Math.max(6, Math.round((item.value / maxVal) * 100)) : 0;
      col.innerHTML =
        '<div class="stats-daily-count">' +
        escapeHtml(String(item.value)) +
        '</div><div class="stats-daily-track"><div class="stats-daily-fill" style="height:' +
        height +
        '%"></div></div><div class="stats-daily-label">' +
        escapeHtml(item.label) +
        "</div>";
      container.appendChild(col);
    });
  }

  function initRangeCollectionStats(lists) {
    const listSel = document.getElementById("stats-range-list");
    const fromInp = document.getElementById("stats-range-from");
    const toInp = document.getElementById("stats-range-to");
    const applyBtn = document.getElementById("stats-range-apply");
    const totalEl = document.getElementById("stats-range-total");
    const chartEl = document.getElementById("stats-range-daily-chart");
    const emptyEl = document.getElementById("stats-range-empty");
    if (!listSel || !fromInp || !toInp || !applyBtn || !totalEl || !chartEl || !emptyEl) return;

    const allOption = document.createElement("option");
    allOption.value = "all";
    allOption.textContent = "Все коллекции";
    listSel.appendChild(allOption);
    (lists || []).forEach(function (lst) {
      const op = document.createElement("option");
      op.value = String(lst.id);
      op.textContent = lst.name || ("Список #" + String(lst.id));
      listSel.appendChild(op);
    });

    const dates = [];
    (lists || []).forEach(function (lst) {
      (lst.movies || []).forEach(function (m) {
        const d = parseIsoDate(m && m.created_at);
        if (d) dates.push(d);
      });
    });
    if (dates.length > 0) {
      dates.sort(function (a, b) {
        return a.getTime() - b.getTime();
      });
      fromInp.value = toYmd(dates[0]);
      toInp.value = toYmd(dates[dates.length - 1]);
    }

    function buildRangeDays(fromDate, toDate) {
      const out = [];
      const cur = new Date(fromDate.getFullYear(), fromDate.getMonth(), fromDate.getDate());
      const end = new Date(toDate.getFullYear(), toDate.getMonth(), toDate.getDate());
      while (cur.getTime() <= end.getTime()) {
        out.push(toYmd(cur));
        cur.setDate(cur.getDate() + 1);
      }
      return out;
    }

    function applyRangeStats() {
      const fromVal = fromInp.value;
      const toVal = toInp.value;
      if (!fromVal || !toVal) return;
      if (fromVal > toVal) {
        emptyEl.textContent = 'Дата "От" не может быть больше даты "До".';
        emptyEl.classList.remove("d-none");
        chartEl.innerHTML = "";
        totalEl.textContent = "0";
        return;
      }

      const selected = listSel.value || "all";
      const rangeDays = buildRangeDays(new Date(fromVal), new Date(toVal));
      const dayMap = {};
      rangeDays.forEach(function (day) {
        dayMap[day] = 0;
      });

      const sourceLists =
        selected === "all"
          ? lists
          : (lists || []).filter(function (lst) {
              return String(lst.id) === selected;
            });

      (sourceLists || []).forEach(function (lst) {
        (lst.movies || []).forEach(function (m) {
          const d = parseIsoDate(m && m.created_at);
          const ymd = d ? toYmd(d) : "";
          if (ymd && dayMap[ymd] != null) dayMap[ymd] += 1;
        });
      });

      const rows = rangeDays.map(function (d) {
        return { label: d.slice(5), value: dayMap[d] || 0 };
      });
      const total = rows.reduce(function (acc, x) {
        return acc + x.value;
      }, 0);
      totalEl.textContent = String(total);

      if (total <= 0) {
        emptyEl.textContent = "Нет добавлений в выбранном диапазоне.";
        emptyEl.classList.remove("d-none");
        chartEl.innerHTML = "";
        return;
      }
      emptyEl.classList.add("d-none");
      renderDailyColumns(chartEl, rows);
    }

    applyBtn.addEventListener("click", applyRangeStats);
    applyRangeStats();
  }

  async function initProfileStatistics() {
    const page = document.querySelector('.users-page[data-page="me"][data-profile-mode="me"]');
    if (!page) return;

    const loading = document.getElementById("profile-stats-loading");
    const content = document.getElementById("profile-stats-content");
    const lists = parseListsData();
    const allMovies = [];
    (lists || []).forEach(function (lst) {
      (lst.movies || []).forEach(function (m) {
        allMovies.push(m);
      });
    });

    const genreMap = new Map();
    allMovies.forEach(function (m) {
      (m.genres || []).forEach(function (g) {
        const label = String(g || "").trim();
        if (!label) return;
        genreMap.set(label, (genreMap.get(label) || 0) + 1);
      });
    });
    const topGenres = Array.from(genreMap.entries())
      .map(function (it) {
        return { label: it[0], value: it[1] };
      })
      .sort(function (a, b) {
        return b.value - a.value;
      })
      .slice(0, 10);
    const genresEmpty = document.getElementById("profile-stats-genres-empty");
    if (topGenres.length > 0) {
      buildBars(
        document.getElementById("profile-stats-genres"),
        topGenres,
        topGenres[0].value
      );
      if (genresEmpty) genresEmpty.classList.add("d-none");
    } else if (genresEmpty) {
      genresEmpty.classList.remove("d-none");
    }

    const typeMap = new Map();
    allMovies.forEach(function (m) {
      const label = movieTypeLabel(m.type) || "Неизвестно";
      typeMap.set(label, (typeMap.get(label) || 0) + 1);
    });
    const typeItems = Array.from(typeMap.entries())
      .map(function (it) {
        return { label: it[0], value: it[1] };
      })
      .sort(function (a, b) {
        return b.value - a.value;
      });
    const typesEmpty = document.getElementById("profile-stats-types-empty");
    if (typeItems.length > 0) {
      renderTypesPie(
        document.getElementById("profile-stats-types-pie"),
        document.getElementById("profile-stats-types-legend"),
        typeItems
      );
      if (typesEmpty) typesEmpty.classList.add("d-none");
    } else if (typesEmpty) {
      typesEmpty.classList.remove("d-none");
    }

    const avgEl = document.getElementById("profile-stats-rating-avg");
    const ratingsEmpty = document.getElementById("profile-stats-ratings-empty");
    try {
      const destribution = await apiFetch("/rating/destribution", { method: "GET" });
      const items = [];
      for (let i = 1; i <= 10; i += 1) {
        const val = Number(destribution && destribution[String(i)]) || 0;
        items.push({ label: String(i), value: val });
      }
      const ratedTotal = items.reduce(function (acc, x) {
        return acc + x.value;
      }, 0);
      const ratedSum = items.reduce(function (acc, x) {
        return acc + Number(x.label) * x.value;
      }, 0);
      if (avgEl) {
        avgEl.textContent = ratedTotal > 0 ? (ratedSum / ratedTotal).toFixed(2) : "—";
      }
      if (ratedTotal > 0) {
        const maxCount = items.reduce(function (acc, x) {
          return Math.max(acc, x.value);
        }, 0);
        buildBars(document.getElementById("profile-stats-ratings"), items, maxCount);
        if (ratingsEmpty) ratingsEmpty.classList.add("d-none");
      } else if (ratingsEmpty) {
        ratingsEmpty.classList.remove("d-none");
      }
    } catch {
      if (avgEl) avgEl.textContent = "—";
      if (ratingsEmpty) ratingsEmpty.classList.remove("d-none");
    } finally {
      initRangeCollectionStats(lists);
      if (loading) loading.classList.add("d-none");
      if (content) content.classList.remove("d-none");
    }
  }

  function initProfileTabs() {
    const tabBar = document.querySelector(".profile-tabs");
    if (!tabBar) return;

    const buttons = tabBar.querySelectorAll("[data-profile-tab]");
    const panelLists = document.getElementById("profile-tab-lists");
    const panelComments = document.getElementById("profile-tab-comments");
    const panelStats = document.getElementById("profile-tab-stats");

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        const tab = btn.getAttribute("data-profile-tab");
        buttons.forEach(function (b) {
          b.classList.toggle("active", b === btn);
          b.setAttribute("aria-selected", b === btn ? "true" : "false");
        });
        if (tab === "lists") {
          if (panelLists) panelLists.classList.remove("d-none");
          if (panelComments) panelComments.classList.add("d-none");
          if (panelStats) panelStats.classList.add("d-none");
        } else if (tab === "comments") {
          if (panelLists) panelLists.classList.add("d-none");
          if (panelComments) panelComments.classList.remove("d-none");
          if (panelStats) panelStats.classList.add("d-none");
          if (!commentsStarted) {
            commentsStarted = true;
            startCommentsPagination();
          }
        } else if (tab === "stats") {
          if (panelLists) panelLists.classList.add("d-none");
          if (panelComments) panelComments.classList.add("d-none");
          if (panelStats) panelStats.classList.remove("d-none");
          if (!statsStarted) {
            statsStarted = true;
            initProfileStatistics();
          }
        }
      });
    });
  }

  function getBootstrapModal(el) {
    if (!el || !window.bootstrap || !window.bootstrap.Modal) return null;
    return window.bootstrap.Modal.getOrCreateInstance(el);
  }

  function initProfileModeration() {
    const page = document.querySelector('.users-page[data-page="user-profile"]');
    if (!page) return;

    const flash = document.getElementById("users-flash");
    const profileId = page.getAttribute("data-user-id");
    const viewerIsAdmin = page.getAttribute("data-viewer-is-admin") === "true";

    const reportBtn = document.getElementById("profile-report-btn");
    const reportModalEl = document.getElementById("profile-report-modal");
    const reportForm = document.getElementById("profile-report-form");
    const reportReason = document.getElementById("profile-report-reason");
    const reportModal = getBootstrapModal(reportModalEl);

    if (reportBtn && reportForm && reportReason && profileId) {
      reportBtn.addEventListener("click", function () {
        reportReason.value = "";
        if (reportModal) reportModal.show();
      });

      reportForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const reason = reportReason.value.trim();
        if (!reason) return;
        hideFlash(flash);
        try {
          await apiFetch("/users/" + encodeURIComponent(profileId) + "/report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ reason: reason }),
          });
          if (reportModal) reportModal.hide();
          showFlash(flash, "Жалоба отправлена", "alert-success");
        } catch (err) {
          showFlash(flash, err.message || "Не удалось отправить жалобу", "alert-danger");
        }
      });
    }

    if (!viewerIsAdmin || !profileId) return;

    const blockBtn = document.getElementById("profile-block-btn");
    const removeAvatarBtn = document.getElementById("profile-remove-avatar-btn");
    const blockModalEl = document.getElementById("profile-block-modal");
    const blockForm = document.getElementById("profile-block-form");
    const blockReason = document.getElementById("profile-block-reason");
    const blockEndsAt = document.getElementById("profile-block-ends-at");
    const blockModal = getBootstrapModal(blockModalEl);

    if (blockBtn && blockForm && blockReason) {
      blockBtn.addEventListener("click", function () {
        blockReason.value = "";
        if (blockEndsAt) blockEndsAt.value = "";
        if (blockModal) blockModal.show();
      });

      blockForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const reason = blockReason.value.trim();
        if (!reason) return;
        hideFlash(flash);

        const payload = {
          user_id: profileId,
          reason: reason,
          ends_at: blockEndsAt && blockEndsAt.value ? new Date(blockEndsAt.value).toISOString() : null,
        };

        try {
          await apiFetch("/admin/blockings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          if (blockModal) blockModal.hide();
          window.location.reload();
        } catch (err) {
          showFlash(flash, err.message || "Не удалось создать блокировку", "alert-danger");
        }
      });
    }

    page.addEventListener("click", async function (e) {
      const btn = e.target.closest(".js-unblock-btn");
      if (!btn) return;
      const blockingId = btn.getAttribute("data-blocking-id");
      if (!blockingId) return;
      if (!window.confirm("Снять эту блокировку?")) return;
      hideFlash(flash);
      try {
        await apiFetch("/admin/blockings/" + encodeURIComponent(blockingId), {
          method: "DELETE",
        });
        window.location.reload();
      } catch (err) {
        showFlash(flash, err.message || "Не удалось снять блокировку", "alert-danger");
      }
    });

    if (removeAvatarBtn) {
      removeAvatarBtn.addEventListener("click", async function () {
        if (!window.confirm("Удалить аватар этого пользователя?")) return;
        hideFlash(flash);
        try {
          await apiFetch("/users/" + encodeURIComponent(profileId) + "/avatar", {
            method: "DELETE",
          });
          window.location.reload();
        } catch (err) {
          showFlash(flash, err.message || "Не удалось удалить аватар", "alert-danger");
        }
      });
    }
  }

  function initMePage() {
    const page = document.getElementById("me-page");
    if (!page) return;

    const flash = document.getElementById("users-flash");

    document
      .getElementById("me-edit-form")
      ?.addEventListener("submit", async function (e) {
        e.preventDefault();
        hideFlash(flash);
        const username = document.getElementById("me-username").value.trim();
        const email = document.getElementById("me-email").value.trim();
        try {
          await apiFetch("/me", {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: username || null, email: email || null }),
          });
          showFlash(flash, "Данные сохранены", "alert-success");
        } catch (err) {
          showFlash(flash, err.message, "alert-danger");
        }
      });

    document.getElementById("me-delete-account")?.addEventListener("click", async function () {
      if (!window.confirm("Удалить аккаунт безвозвратно?")) return;
      try {
        await apiFetch("/me", { method: "DELETE" });
        window.location.href = "/";
      } catch (err) {
        showFlash(flash, err.message, "alert-danger");
      }
    });

    document.getElementById("me-remove-avatar")?.addEventListener("click", async function () {
      if (!window.confirm("Удалить текущий аватар?")) return;
      try {
        await apiFetch("/me/avatar", { method: "DELETE" });
        window.location.reload();
      } catch (err) {
        showFlash(flash, err.message, "alert-danger");
      }
    });

    document
      .getElementById("me-new-list-form")
      ?.addEventListener("submit", async function (e) {
        e.preventDefault();
        hideFlash(flash);
        const name = document.getElementById("new-list-name").value.trim();
        const isPublic = document.getElementById("new-list-public").checked;
        try {
          await apiFetch("/list", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name, is_public: isPublic }),
          });
          window.location.reload();
        } catch (err) {
          showFlash(flash, err.message, "alert-danger");
        }
      });

    document.getElementById("me-send-email-confirm")?.addEventListener("click", async function () {
      const msg = document.getElementById("me-email-confirm-msg");
      try {
        await apiFetch("/send_confirmation", { method: "GET" });
        if (msg) {
          msg.textContent = "Письмо отправлено. Проверьте почту.";
          msg.classList.remove("d-none");
          msg.classList.add("text-success");
        }
      } catch (err) {
        if (msg) {
          msg.textContent = err.message;
          msg.classList.remove("d-none");
          msg.classList.add("text-danger");
        }
      }
    });

    document.getElementById("me-google-email-connect")?.addEventListener("click", async function () {
      const msg = document.getElementById("me-email-confirm-msg");
      const clientId = (page.getAttribute("data-google-oauth-client-id") || "").trim();
      if (!clientId) {
        if (msg) {
          msg.textContent = "Google OAuth не настроен на сервере.";
          msg.classList.remove("d-none");
          msg.classList.add("text-danger");
        }
        return;
      }
      if (!window.google || !window.google.accounts || !window.google.accounts.oauth2) {
        if (msg) {
          msg.textContent = "Не удалось загрузить Google OAuth. Обновите страницу.";
          msg.classList.remove("d-none");
          msg.classList.add("text-danger");
        }
        return;
      }
      if (msg) {
        msg.textContent = "Открываем Google OAuth...";
        msg.classList.remove("d-none");
        msg.classList.remove("text-danger");
      }

      try {
        const accessToken = await new Promise(function (resolve, reject) {
          const tokenClient = window.google.accounts.oauth2.initTokenClient({
            client_id: clientId,
            scope: "openid email profile",
            callback: function (tokenResponse) {
              if (!tokenResponse || tokenResponse.error || !tokenResponse.access_token) {
                reject(new Error("Google OAuth вернул ошибку"));
                return;
              }
              resolve(tokenResponse.access_token);
            },
          });
          tokenClient.requestAccessToken({ prompt: "consent" });
        });

        const googleResp = await fetch("https://www.googleapis.com/oauth2/v3/userinfo", {
          method: "GET",
          headers: { Authorization: "Bearer " + accessToken },
        });
        if (!googleResp.ok) {
          throw new Error("Не удалось получить данные Google-почты");
        }
        const googleData = await googleResp.json();
        const email = googleData && googleData.email ? String(googleData.email).trim() : "";
        if (!email) {
          throw new Error("Google не вернул email");
        }

        await apiFetch("/confirm_email/oauth", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email }),
        });

        if (msg) {
          msg.textContent = "Почта подтверждена через Google.";
          msg.classList.remove("text-danger");
          msg.classList.add("text-success");
        }
        window.location.reload();
      } catch (err) {
        if (msg) {
          msg.textContent = err.message || "Не удалось подтвердить почту через Google";
          msg.classList.remove("d-none");
          msg.classList.add("text-danger");
        }
      }
    });

    document.getElementById("me-send-password-code")?.addEventListener("click", async function () {
      const msg = document.getElementById("me-password-msg");
      try {
        await apiFetch("/send_password_confirmation", { method: "GET" });
        if (msg) {
          msg.textContent = "Код отправлен на почту.";
          msg.classList.remove("d-none");
          msg.classList.remove("text-danger");
          msg.classList.add("text-success");
        }
      } catch (err) {
        if (msg) {
          msg.textContent = err.message;
          msg.classList.remove("d-none");
          msg.classList.add("text-danger");
        }
      }
    });

    document
      .getElementById("me-change-password-form")
      ?.addEventListener("submit", async function (e) {
        e.preventDefault();
        const msg = document.getElementById("me-password-msg");
        const code = document.getElementById("me-pwd-code").value.trim();
        const p1 = document.getElementById("me-pwd-new").value;
        const p2 = document.getElementById("me-pwd-new2").value;
        if (p1 !== p2) {
          if (msg) {
            msg.textContent = "Пароли не совпадают";
            msg.classList.remove("d-none");
            msg.classList.add("text-danger");
          }
          return;
        }
        if (!code) {
          if (msg) {
            msg.textContent = "Введите код из письма";
            msg.classList.remove("d-none");
            msg.classList.add("text-danger");
          }
          return;
        }
        try {
          const q = encodeURIComponent(code);
          await apiFetch("/change_password?code=" + q, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ password: p1 }),
          });
          if (msg) {
            msg.textContent = "Пароль изменён.";
            msg.classList.remove("d-none");
            msg.classList.remove("text-danger");
            msg.classList.add("text-success");
          }
        } catch (err) {
          if (msg) {
            msg.textContent = err.message;
            msg.classList.remove("d-none");
            msg.classList.add("text-danger");
          }
        }
      });
  }

  function initAccountEmailPage() {
    const root = document.querySelector('[data-page="account-email"]');
    if (!root) return;
    document.getElementById("account-email-send")?.addEventListener("click", async function () {
      const msg = document.getElementById("account-email-msg");
      try {
        await apiFetch("/send_confirmation", { method: "GET" });
        if (msg) {
          msg.textContent = "Письмо отправлено.";
          msg.classList.remove("d-none");
        }
      } catch (err) {
        if (msg) {
          msg.textContent = err.message;
          msg.classList.remove("d-none");
        }
      }
    });
  }

  function initAccountPasswordPage() {
    const root = document.querySelector('[data-page="account-password"]');
    if (!root) return;
    document
      .getElementById("account-password-send-code")
      ?.addEventListener("click", async function () {
        const msg = document.getElementById("account-password-msg");
        try {
          await apiFetch("/send_password_confirmation", { method: "GET" });
          if (msg) {
            msg.textContent = "Код отправлен на почту.";
            msg.classList.remove("d-none");
          }
        } catch (err) {
          if (msg) {
            msg.textContent = err.message;
            msg.classList.remove("d-none");
          }
        }
      });
    document.getElementById("account-password-form")?.addEventListener("submit", async function (e) {
      e.preventDefault();
      const msg = document.getElementById("account-password-msg");
      const code = document.getElementById("acc-pwd-code").value.trim();
      const p1 = document.getElementById("acc-pwd-new").value;
      const p2 = document.getElementById("acc-pwd-new2").value;
      if (p1 !== p2) {
        if (msg) {
          msg.textContent = "Пароли не совпадают";
          msg.classList.remove("d-none");
        }
        return;
      }
      if (!code) {
        if (msg) {
          msg.textContent = "Введите код";
          msg.classList.remove("d-none");
        }
        return;
      }
      try {
        const q = encodeURIComponent(code);
        await apiFetch("/change_password?code=" + q, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ password: p1 }),
        });
        if (msg) {
          msg.textContent = "Пароль изменён.";
          msg.classList.remove("d-none");
        }
      } catch (err) {
        if (msg) {
          msg.textContent = err.message;
          msg.classList.remove("d-none");
        }
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initProfileTabs();
    initProfileLists();
    initProfileModeration();
    initMePage();
    initAccountEmailPage();
    initAccountPasswordPage();
  });
})();
