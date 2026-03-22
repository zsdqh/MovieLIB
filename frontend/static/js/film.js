/**
 * Страница фильма: списки (добавить / удалить), оценка.
 */
(function () {
  const root = document.getElementById("film-page");
  if (!root) return;

  const movieId = parseInt(root.getAttribute("data-movie-id") || "0", 10);
  const dataEl = document.getElementById("film-user-lists-data");
  const select = document.getElementById("film-list-select");
  const btn = document.getElementById("film-add-to-list-btn");
  const msg = document.getElementById("film-add-list-msg");
  const removeWrap = document.getElementById("film-remove-list-wrap");
  const removeSelect = document.getElementById("film-remove-list-select");
  const removeBtn = document.getElementById("film-remove-from-list-btn");

  const ratingInput = document.getElementById("film-user-rating-input");
  const ratingSave = document.getElementById("film-user-rating-save");
  const ratingClear = document.getElementById("film-user-rating-clear");
  const ratingMsg = document.getElementById("film-user-rating-msg");

  let lists = [];
  try {
    lists = JSON.parse(dataEl && dataEl.textContent ? dataEl.textContent : "[]");
  } catch {
    lists = [];
  }

  function listContainsMovie(lst, mid) {
    return (lst.movies || []).some(function (m) {
      return m && Number(m.id) === mid;
    });
  }

  function refreshRemoveBlock() {
    if (!removeWrap || !removeSelect || !removeBtn) return;
    removeSelect.innerHTML = '<option value="">— выберите список —</option>';
    let any = false;
    lists.forEach(function (lst) {
      if (listContainsMovie(lst, movieId)) {
        any = true;
        const opt = document.createElement("option");
        opt.value = String(lst.id);
        opt.textContent = (lst.name || "Список") + " (" + ((lst.movies || []).length) + ")";
        removeSelect.appendChild(opt);
      }
    });
    removeWrap.classList.toggle("d-none", !any);
    removeBtn.disabled = !removeSelect.value;
  }

  if (select && btn && dataEl) {
    lists.forEach(function (lst) {
      const opt = document.createElement("option");
      opt.value = String(lst.id);
      opt.textContent = (lst.name || "Список") + " (" + ((lst.movies || []).length) + ")";
      select.appendChild(opt);
    });

    select.addEventListener("change", function () {
      btn.disabled = !select.value;
    });

    if (removeSelect) {
      removeSelect.addEventListener("change", function () {
        removeBtn.disabled = !removeSelect.value;
      });
    }

    refreshRemoveBlock();
  }

  function showMsg(text, isError) {
    if (!msg) return;
    msg.textContent = text;
    msg.classList.remove("d-none", "text-danger", "text-success", "text-muted");
    msg.classList.add(isError ? "text-danger" : "text-success");
  }

  function showRatingMsg(text, variant) {
    if (!ratingMsg) return;
    ratingMsg.textContent = text;
    ratingMsg.classList.remove("d-none", "text-danger", "text-success", "text-muted");
    if (variant === "muted") ratingMsg.classList.add("text-muted");
    else if (variant === "ok") ratingMsg.classList.add("text-success");
    else if (variant === "bad") ratingMsg.classList.add("text-danger");
    else ratingMsg.classList.add("text-muted");
  }

  if (btn) {
    btn.addEventListener("click", function () {
      const listId = select && select.value;
      if (!listId || !movieId) return;
      btn.disabled = true;
      fetch("/list/" + encodeURIComponent(listId) + "/movies", {
        method: "POST",
        credentials: "include",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ movie_id: movieId }),
      })
        .then(function (res) {
          if (res.status === 401) {
            window.location.href = "/login";
            return;
          }
          if (!res.ok) {
            return res.json().then(function (d) {
              throw new Error(d.detail || d.message || "Ошибка");
            });
          }
          return res.json();
        })
        .then(function (updated) {
          if (!updated) return;
          const idStr = String(updated.id);
          const idx = lists.findIndex(function (l) {
            return String(l.id) === idStr;
          });
          if (idx >= 0) lists[idx] = updated;
          showMsg("Фильм добавлен в список.", false);
          refreshRemoveBlock();
        })
        .catch(function (e) {
          showMsg(e.message || "Не удалось добавить", true);
        })
        .finally(function () {
          btn.disabled = !(select && select.value);
        });
    });
  }

  if (removeBtn && removeSelect) {
    removeBtn.addEventListener("click", function () {
      const listId = removeSelect.value;
      if (!listId || !movieId) return;
      removeBtn.disabled = true;
      fetch("/list/" + encodeURIComponent(listId) + "/movies", {
        method: "DELETE",
        credentials: "include",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ movie_id: movieId }),
      })
        .then(function (res) {
          if (res.status === 401) {
            window.location.href = "/login";
            return;
          }
          if (!res.ok) {
            return res.json().then(function (d) {
              throw new Error(d.detail || d.message || "Ошибка");
            });
          }
          return res.json();
        })
        .then(function (updated) {
          if (!updated) return;
          const idStr = String(updated.id);
          const idx = lists.findIndex(function (l) {
            return String(l.id) === idStr;
          });
          if (idx >= 0) lists[idx] = updated;
          showMsg("Фильм удалён из списка.", false);
          refreshRemoveBlock();
        })
        .catch(function (e) {
          showMsg(e.message || "Не удалось удалить", true);
        })
        .finally(function () {
          removeBtn.disabled = !removeSelect.value;
        });
    });
  }

  function loadMyRating() {
    if (!ratingInput) return;
    fetch("/rating/movie?movie_id=" + encodeURIComponent(String(movieId)), {
      credentials: "include",
      headers: { Accept: "application/json" },
    })
      .then(function (res) {
        if (res.status === 401) return null;
        if (!res.ok) return null;
        return res.json();
      })
      .then(function (data) {
        if (data && data.rating != null && Number.isFinite(Number(data.rating))) {
          ratingInput.value = String(data.rating);
        }
      })
      .catch(function () {});
  }

  if (ratingSave && ratingClear && ratingInput) {
    loadMyRating();

    ratingSave.addEventListener("click", function () {
      const raw = ratingInput.value.trim();
      const n = parseInt(raw, 10);
      if (!Number.isFinite(n) || n < 1 || n > 10) {
        showRatingMsg("Введите целое число от 1 до 10.", "bad");
        return;
      }
      ratingSave.disabled = true;
      fetch("/rating/movie", {
        method: "POST",
        credentials: "include",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ movie_id: movieId, rating: n }),
      })
        .then(function (res) {
          if (res.status === 401) {
            window.location.href = "/login";
            return;
          }
          if (!res.ok) {
            return res.json().then(function (d) {
              throw new Error(
                (Array.isArray(d.detail) ? d.detail[0] && d.detail[0].msg : null) ||
                  d.detail ||
                  "Ошибка"
              );
            });
          }
          window.location.reload();
        })
        .catch(function (e) {
          showRatingMsg(e.message || "Не удалось сохранить", "bad");
        })
        .finally(function () {
          ratingSave.disabled = false;
        });
    });

    ratingClear.addEventListener("click", function () {
      ratingClear.disabled = true;
      fetch("/rating/movie", {
        method: "DELETE",
        credentials: "include",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ movie_id: movieId }),
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
          window.location.reload();
        })
        .catch(function (e) {
          showRatingMsg(e.message || "Не удалось удалить оценку", "bad");
        })
        .finally(function () {
          ratingClear.disabled = false;
        });
    });
  }

  var refreshBtn = document.getElementById("film-page-refresh-btn");
  if (refreshBtn && movieId) {
    refreshBtn.addEventListener("click", function () {
      refreshBtn.disabled = true;
      fetch("/movie/" + encodeURIComponent(String(movieId)) + "/refresh", {
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
          refreshBtn.disabled = false;
        });
    });
  }
})();
