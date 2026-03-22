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
    const col = document.createElement("div");
    col.className = "col-6 col-sm-4 col-md-4 col-lg-3";
    const poster = m.poster || "";
    const name = m.name || "";
    const typeLabel = movieTypeLabel(m.type);
    const removeBtn =
      showRemove ?
        '<button type="button" class="btn btn-sm btn-outline-danger profile-movie-remove" title="Удалить из списка" data-list-id="' +
        escapeAttr(String(opts.listId)) +
        '" data-movie-id="' +
        escapeAttr(String(m.id)) +
        '"><i class="fa-solid fa-xmark" aria-hidden="true"></i></button>'
      : "";
    col.innerHTML =
      '<div class="position-relative profile-movie-card-wrap h-100">' +
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
      movies.forEach(function (m) {
        grid.appendChild(
          renderMovieCard(m, {
            showRemove: Boolean(listIdForRemove),
            listId: listIdForRemove,
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
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className =
          "list-group-item list-group-item-action list-nav-row text-start";
        btn.setAttribute("data-list-key", idStr);
        btn.innerHTML =
          '<div class="list-nav-btn-inner">' +
          '<div class="fw-semibold">' +
          escapeHtml(lst.name) +
          "</div>" +
          '<div class="d-flex flex-wrap align-items-center gap-1 mt-1">' +
          '<span class="text-muted small">(' +
          count +
          ")</span>" +
          listVisibilityBadgeHtml(pub) +
          "</div></div>";
        nav.appendChild(btn);
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

      const viewRow = e.target.closest("button.list-nav-row");
      if (viewRow) {
        const key = viewRow.getAttribute("data-list-key");
        if (key) {
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

  function initProfileTabs() {
    const tabBar = document.querySelector(".profile-tabs");
    if (!tabBar) return;

    const buttons = tabBar.querySelectorAll("[data-profile-tab]");
    const panelLists = document.getElementById("profile-tab-lists");
    const panelComments = document.getElementById("profile-tab-comments");

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
        } else if (tab === "comments") {
          if (panelLists) panelLists.classList.add("d-none");
          if (panelComments) panelComments.classList.remove("d-none");
          if (!commentsStarted) {
            commentsStarted = true;
            startCommentsPagination();
          }
        }
      });
    });
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
    initMePage();
    initAccountEmailPage();
    initAccountPasswordPage();
  });
})();
