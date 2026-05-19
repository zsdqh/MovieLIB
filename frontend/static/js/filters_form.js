/**
 * Форма FilmParams: сбор query string и переход на GET /filter
 * + автодополнение поля «Персона» с поиском через /search/person
 */
(function () {
  const form = document.getElementById("film-filters-form");
  if (!form) return;

  // ===== Сортировка (оставлено без изменений) =====
  const sortContainer = document.getElementById("ff-sort-container");
  const addSortBtn = document.getElementById("ff-add-sort");

  if (addSortBtn && sortContainer) {
    addSortBtn.addEventListener("click", function () {
      const row = document.createElement("div");
      row.className = "d-flex gap-2";

      row.innerHTML = `
        <select class="form-select ff-sort-field">
          <option value="">Поле</option>
          ${Array.from(document.querySelectorAll(".ff-sort-field option"))
            .map(o => `<option value="${o.value}">${o.textContent}</option>`)
            .join("")}
        </select>

        <select class="form-select ff-sort-order">
          <option value="+">↑ По возрастанию</option>
          <option value="-">↓ По убыванию</option>
        </select>

        <button type="button" class="btn btn-outline-danger ff-remove-sort">×</button>
      `;

      sortContainer.appendChild(row);
    });

    sortContainer.addEventListener("click", function (e) {
      if (e.target.classList.contains("ff-remove-sort")) {
        e.target.parentElement.remove();
      }
    });
  }

  // ===== НОВОЕ: автодополнение персоны =====
  const personSearchInput = document.getElementById("ff-person-search");
  const personHiddenInput = document.getElementById("ff-person");
  const suggestionsList = document.getElementById("ff-person-suggestions");
  let debounceTimer = null;
  let currentRequest = null;  // Для отмены fetch при новом вводе
  let selectedIndex = -1;     // Для навигации клавишами

  // Функция debounce
  function debounce(fn, delay) {
    return function(...args) {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  // Рендер подсказок
  function renderSuggestions(persons) {
    suggestionsList.innerHTML = "";
    if (!persons || persons.length === 0) {
      const li = document.createElement("li");
      li.className = "suggestion-no-results";
      li.textContent = "Ничего не найдено";
      suggestionsList.appendChild(li);
    } else {
      persons.forEach((p, idx) => {
        const li = document.createElement("li");
        li.className = "suggestion-item";
        li.dataset.id = p.id;
        li.dataset.name = p.name;
        li.innerHTML = `
          <img src="${p.photo || '/static/img/no-photo.png'}" alt="" onerror="this.style.display='none'">
          <span>${escapeHtml(p.name)}</span>
        `;
        li.addEventListener("mousedown", function(e) {
          e.preventDefault(); // чтобы не сработал blur раньше клика
          selectPerson(p.id, p.name);
        });
        suggestionsList.appendChild(li);
      });
    }
    selectedIndex = -1;
    suggestionsList.style.display = "block";
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Выбор персоны из списка
  function selectPerson(id, name) {
    personHiddenInput.value = id;
    personSearchInput.value = name;
    hideSuggestions();
  }

  // Скрытие списка
  function hideSuggestions() {
    suggestionsList.style.display = "none";
    selectedIndex = -1;
  }

  // Загрузка подсказок с сервера
  function fetchPersons(query) {
    if (!query.trim()) {
      hideSuggestions();
      return;
    }

    // Отмена предыдущего запроса, если он ещё не завершён
    if (currentRequest) {
      currentRequest.abort();
    }

    const controller = new AbortController();
    currentRequest = controller;

    fetch(`/search/person?query=${encodeURIComponent(query.trim())}`, {
      signal: controller.signal,
      headers: { "Accept": "application/json" }
    })
      .then(res => {
        if (!res.ok) throw new Error("Network error");
        return res.json();
      })
      .then(data => {
        if (controller.signal.aborted) return;
        currentRequest = null;
        const persons = data.persons || [];
        renderSuggestions(persons);
      })
      .catch(err => {
        if (err.name === "AbortError") return; // отмена – нормально
        console.error("Ошибка поиска персон:", err);
        currentRequest = null;
        suggestionsList.innerHTML = `<li class="suggestion-no-results">Ошибка загрузки</li>`;
        suggestionsList.style.display = "block";
      });
  }

  // debounce-версия запроса
  const debouncedFetch = debounce(fetchPersons, 500);

  // Обработчик ввода в поле поиска
  personSearchInput.addEventListener("input", function() {
    const query = this.value;
    debouncedFetch(query);
  });

  // Навигация клавиатурой (стрелки, Enter, Escape)
  personSearchInput.addEventListener("keydown", function(e) {
    const items = suggestionsList.querySelectorAll(".suggestion-item");
    if (!items.length || suggestionsList.style.display === "none") return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
      updateActiveItem(items);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      selectedIndex = Math.max(selectedIndex - 1, 0);
      updateActiveItem(items);
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (selectedIndex >= 0 && items[selectedIndex]) {
        const li = items[selectedIndex];
        selectPerson(li.dataset.id, li.dataset.name);
      }
    } else if (e.key === "Escape") {
      hideSuggestions();
    }
  });

  function updateActiveItem(items) {
    items.forEach((item, i) => {
      item.classList.toggle("active", i === selectedIndex);
    });
    // Прокрутка к выбранному элементу
    if (selectedIndex >= 0 && items[selectedIndex]) {
      items[selectedIndex].scrollIntoView({ block: "nearest" });
    }
  }

  // Скрытие списка при клике вне компонента
  document.addEventListener("click", function(e) {
    if (!personSearchInput.contains(e.target) && !suggestionsList.contains(e.target)) {
      hideSuggestions();
    }
  });

  // При потере фокуса скрываем с небольшой задержкой, чтобы успел сработать клик по элементу
  personSearchInput.addEventListener("blur", function() {
    setTimeout(() => {
      if (!suggestionsList.contains(document.activeElement)) {
        hideSuggestions();
      }
    }, 150);
  });

  // Инициализация: если скрытое поле уже содержит ID (например, из person_id параметра),
  // пытаемся получить имя и фото персоны и отобразить в поле
  (function initPersonField() {
    const initialId = personHiddenInput.value.trim();
    if (!initialId) return;

    // Показываем временную надпись
    personSearchInput.value = "Загрузка...";

    fetch(`/person/${initialId}/`, {
      headers: { "Accept": "application/json" }
    })
      .then(res => res.json())
      .then(data => {
        if (data && data.name) {
          personSearchInput.value = data.name;
        } else {
          throw new Error("No data");
        }
      })
      .catch(() => {
        // Если API недоступен или ошибка, показываем просто ID
        personSearchInput.value = ``;
      });
  })();

  // ===== Обработка отправки формы (без изменений, но person_id теперь из скрытого поля) =====
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const params = new URLSearchParams();
    params.set("page", "1");

    const year = document.getElementById("ff-year");
    const rating = document.getElementById("ff-rating");
    const series = document.getElementById("ff-series");
    const person = document.getElementById("ff-person");   // теперь это hidden, id="ff-person"
    const countriesRaw = document.getElementById("ff-countries");
    const genresSelect = document.getElementById("ff-genres");
    const typesSelect = document.getElementById("ff-types");
    const genresAdv = document.getElementById("ff-genres-adv");
    const typesAdv = document.getElementById("ff-types-adv");

    if (year && year.value.trim()) params.set("year", year.value.trim());
    if (rating && rating.value.trim()) params.set("rating", rating.value.trim());
    if (series && (series.value === "true" || series.value === "false")) {
      params.set("is_series", series.value);
    }

    // person.value теперь строка с ID, парсим как целое
    if (person && person.value.trim()) {
      const n = parseInt(person.value.trim(), 10);
      if (!Number.isNaN(n) && n > 0) params.set("person_id", String(n));
    }

    if (countriesRaw && countriesRaw.value.trim()) {
      countriesRaw.value
        .split(/[,;\n]+/)
        .map(function (s) { return s.trim(); })
        .filter(Boolean)
        .forEach(function (c) { params.append("countries", c); });
    }

    const advG = genresAdv && genresAdv.value.trim();
    if (advG) {
      advG.split("\n").forEach(function (line) {
        const t = line.trim();
        if (t) params.append("genres", t);
      });
    } else if (genresSelect) {
      Array.from(genresSelect.selectedOptions).forEach(function (opt) {
        params.append("genres", opt.value);
      });
    }

    const advT = typesAdv && typesAdv.value.trim();
    if (advT) {
      advT.split("\n").forEach(function (line) {
        const t = line.trim();
        if (t) params.append("type_number", t);
      });
    } else if (typesSelect) {
      Array.from(typesSelect.selectedOptions).forEach(function (opt) {
        params.append("type_number", opt.value);
      });
    }

    const sortFields = document.querySelectorAll("#ff-sort-container > div");
    sortFields.forEach(function (row) {
      const field = row.querySelector(".ff-sort-field");
      const order = row.querySelector(".ff-sort-order");
      if (field && order && field.value) {
        params.append("order_by", order.value + field.value);
      }
    });

    window.location.href = "/filter?" + params.toString();
  });
})();
