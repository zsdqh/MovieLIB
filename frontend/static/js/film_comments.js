/**
 * Страница комментариев к фильму: загрузка, ответы, реакции, ссылки на профили.
 */
(function () {
  const pageRoot = document.getElementById("film-comments-page");
  if (!pageRoot) return;

  const movieId = pageRoot.getAttribute("data-movie-id");
  const root = document.getElementById("film-comments-root");
  const emptyEl = document.getElementById("film-comments-empty");
  const moreBtn = document.getElementById("film-comments-more");
  const flash = document.getElementById("film-comments-flash");
  const form = document.getElementById("film-comment-form");
  const answerToInput = document.getElementById("film-comment-answer-to");
  const replyBanner = document.getElementById("film-comment-reply-banner");
  const replyText = document.getElementById("film-comment-reply-text");
  const replyCancel = document.getElementById("film-comment-reply-cancel");

  let nextPage = 0;
  let loading = false;
  let haveNext = false;

  function userProfileHref(user) {
    if (!user || !user.id) return null;
    return "/users/" + encodeURIComponent(String(user.id));
  }

  function formatDt(iso) {
    if (!iso) return "";
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

  function ratingClass(n) {
    if (!Number.isFinite(n) || n === 0) return "comment-rating-num--zero";
    if (n > 0) return "comment-rating-num--pos";
    return "comment-rating-num--neg";
  }

  function formatRatingText(rating) {
    const n = Number(rating);
    if (!Number.isFinite(n) || n === 0) return "0";
    if (n > 0) return "+" + n;
    return String(n);
  }

  function applyCommentUpdate(commentEl, data) {
    if (!commentEl || !data) return;
    const scoreEl = commentEl.querySelector(".comment-rating-num");
    if (scoreEl) {
      scoreEl.textContent = formatRatingText(data.rating);
      scoreEl.className =
        "comment-rating-num btn btn-link p-0 align-baseline text-decoration-none " +
        ratingClass(Number(data.rating));
    }
  }

  function renderComment(c, depth) {
    depth = depth || 0;
    const wrap = document.createElement("div");
    const art = document.createElement("article");
    art.className = "card comment-card-film";
    art.setAttribute("data-comment-id", String(c.id));
    if (depth > 0) {
      art.classList.add("comment-nested");
    }

    const user = c.user || {};
    const href = userProfileHref(user);

    const avatarCol = document.createElement("div");
    avatarCol.className = "flex-shrink-0";
    if (user.avatar_url) {
      const img = document.createElement("img");
      img.src = user.avatar_url;
      img.alt = "";
      img.className = "rounded-circle";
      img.width = 40;
      img.height = 40;
      avatarCol.appendChild(img);
    } else {
      const ph = document.createElement("span");
      ph.className =
        "rounded-circle bg-secondary d-inline-flex align-items-center justify-content-center text-white small";
      ph.style.width = "40px";
      ph.style.height = "40px";
      ph.innerHTML = '<i class="fa-solid fa-user"></i>';
      avatarCol.appendChild(ph);
    }

    const bodyCol = document.createElement("div");
    bodyCol.className = "flex-grow-1";
    bodyCol.style.minWidth = "0";

    const nameRow = document.createElement("div");
    nameRow.className = "small fw-semibold";
    if (href) {
      const a = document.createElement("a");
      a.href = href;
      a.className = "text-reset text-decoration-none comment-user-link";
      a.textContent = user.username || "Пользователь";
      nameRow.appendChild(a);
    } else {
      nameRow.textContent = user.username || "Пользователь";
    }

    const textP = document.createElement("p");
    textP.className = "mb-1 mt-1";
    textP.textContent = c.text || "";

    const meta = document.createElement("p");
    meta.className = "comment-meta mb-0 small text-muted d-flex flex-wrap align-items-center gap-2";

    const dtSpan = document.createElement("span");
    dtSpan.textContent = formatDt(c.created_at);
    meta.appendChild(dtSpan);

    const dot = document.createElement("span");
    dot.textContent = "·";
    meta.appendChild(dot);

    const voteWrap = document.createElement("span");
    voteWrap.className = "d-inline-flex align-items-center comment-vote-wrap";

    const upBtn = document.createElement("button");
    upBtn.type = "button";
    upBtn.className = "btn btn-sm btn-outline-secondary py-0 px-1 comment-vote-btn";
    upBtn.setAttribute("data-action", "like");
    upBtn.setAttribute("data-comment-id", String(c.id));
    upBtn.setAttribute("title", "Лайк");
    upBtn.innerHTML = '<i class="fa-solid fa-chevron-up" aria-hidden="true"></i>';

    const scoreBtn = document.createElement("button");
    scoreBtn.type = "button";
    scoreBtn.className =
      "comment-rating-num btn btn-link p-0 align-baseline text-decoration-none " +
      ratingClass(Number(c.rating));
    scoreBtn.setAttribute("data-action", "clear");
    scoreBtn.setAttribute("data-comment-id", String(c.id));
    scoreBtn.setAttribute("title", "Убрать свою реакцию");
    scoreBtn.textContent = formatRatingText(c.rating);

    const downBtn = document.createElement("button");
    downBtn.type = "button";
    downBtn.className = "btn btn-sm btn-outline-secondary py-0 px-1 comment-vote-btn";
    downBtn.setAttribute("data-action", "dislike");
    downBtn.setAttribute("data-comment-id", String(c.id));
    downBtn.setAttribute("title", "Дизлайк");
    downBtn.innerHTML = '<i class="fa-solid fa-chevron-down" aria-hidden="true"></i>';

    voteWrap.appendChild(upBtn);
    voteWrap.appendChild(scoreBtn);
    voteWrap.appendChild(downBtn);

    meta.appendChild(voteWrap);

    if (form) {
      const replyBtn = document.createElement("button");
      replyBtn.type = "button";
      replyBtn.className = "btn btn-link btn-sm py-0 px-1";
      replyBtn.setAttribute("data-action", "reply");
      replyBtn.setAttribute("data-comment-id", String(c.id));
      replyBtn.setAttribute("data-username", user.username || "");
      replyBtn.textContent = "Ответить";
      meta.appendChild(document.createTextNode(" "));
      meta.appendChild(replyBtn);
    }

    bodyCol.appendChild(nameRow);
    bodyCol.appendChild(textP);
    bodyCol.appendChild(meta);

    const row = document.createElement("div");
    row.className = "d-flex gap-2";
    row.appendChild(avatarCol);
    row.appendChild(bodyCol);

    const cardBody = document.createElement("div");
    cardBody.className = "card-body py-2 px-3";
    cardBody.appendChild(row);
    art.appendChild(cardBody);

    wrap.appendChild(art);

    (c.answers || []).forEach(function (a) {
      wrap.appendChild(renderComment(a, depth + 1));
    });

    return wrap;
  }

  function setEmpty(visible) {
    if (!emptyEl) return;
    emptyEl.classList.toggle("d-none", !visible);
  }

  function setAnswerTo(commentId, username) {
    if (!answerToInput) return;
    if (commentId == null || commentId < 0) {
      answerToInput.value = "-1";
      if (replyBanner) replyBanner.classList.add("d-none");
      return;
    }
    answerToInput.value = String(commentId);
    if (replyBanner && replyText) {
      replyText.textContent =
        "Ответ на комментарий" + (username ? " от " + username : "") + " (#" + commentId + ")";
      replyBanner.classList.remove("d-none");
    }
    const ta = document.getElementById("film-comment-text");
    if (ta) ta.focus();
  }

  if (replyCancel) {
    replyCancel.addEventListener("click", function () {
      setAnswerTo(-1, "");
    });
  }

  function loadPage() {
    if (loading || !movieId) return;
    loading = true;
    hideFlash();
    const url =
      "/movie/" +
      encodeURIComponent(movieId) +
      "/comments?page=" +
      encodeURIComponent(String(nextPage));
    fetch(url, {
      credentials: "include",
      headers: { Accept: "application/json" },
    })
      .then(function (res) {
        if (!res.ok) throw new Error("Не удалось загрузить комментарии");
        return res.json();
      })
      .then(function (data) {
        const list = (data && data.comments) || [];
        haveNext = Boolean(data && data.have_next);
        if (nextPage === 0 && list.length === 0) {
          setEmpty(true);
        } else {
          setEmpty(false);
        }
        list.forEach(function (c) {
          root.appendChild(renderComment(c, 0));
        });
        nextPage += 1;
        if (moreBtn) {
          moreBtn.classList.toggle("d-none", !haveNext);
        }
      })
      .catch(function (e) {
        showFlash(e.message || "Ошибка загрузки");
      })
      .finally(function () {
        loading = false;
      });
  }

  if (moreBtn) {
    moreBtn.addEventListener("click", loadPage);
  }

  if (root) {
    root.addEventListener("click", function (e) {
      const t = e.target.closest("[data-action]");
      if (!t || !root.contains(t)) return;
      const action = t.getAttribute("data-action");
      const cid = t.getAttribute("data-comment-id");
      if (!cid) return;

      if (action === "reply") {
        const uname = t.getAttribute("data-username") || "";
        setAnswerTo(parseInt(cid, 10), uname);
        return;
      }

      if (!action || (action !== "like" && action !== "dislike" && action !== "clear")) return;

      e.preventDefault();
      let method = "POST";
      let path =
        "/comment/" + encodeURIComponent(cid) + "/" + (action === "dislike" ? "dislike" : "like");
      if (action === "clear") {
        method = "DELETE";
        path = "/comment/" + encodeURIComponent(cid) + "/like";
      }

      const card = t.closest(".comment-card-film");
      fetch(path, {
        method: method,
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
              throw new Error(d.detail || "Ошибка");
            });
          }
          return res.json();
        })
        .then(function (data) {
          if (data && card) applyCommentUpdate(card, data);
        })
        .catch(function (err) {
          showFlash(err.message || "Ошибка", "alert-danger");
        });
    });
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const ta = document.getElementById("film-comment-text");
      const text = ta && ta.value.trim();
      if (!text) return;
      const fd = new FormData();
      fd.set("text", text);
      const at = answerToInput ? answerToInput.value : "-1";
      fd.set("answer_to", at || "-1");
      fetch("/movie/" + encodeURIComponent(movieId) + "/comments", {
        method: "POST",
        credentials: "include",
        body: fd,
      })
        .then(function (res) {
          if (res.status === 401) {
            window.location.href = "/login";
            return;
          }
          if (!res.ok) {
            return res.json().then(function (d) {
              throw new Error(d.detail || "Ошибка отправки");
            });
          }
          return res.json();
        })
        .then(function () {
          if (ta) ta.value = "";
          setAnswerTo(-1, "");
          root.innerHTML = "";
          nextPage = 0;
          loadPage();
        })
        .catch(function (err) {
          showFlash(err.message || "Ошибка");
        });
    });
  }

  loadPage();
})();
