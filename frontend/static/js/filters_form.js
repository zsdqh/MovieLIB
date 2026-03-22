/**
 * Форма FilmParams: сбор query string и переход на GET /filter
 */
(function () {
  const form = document.getElementById("film-filters-form");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const params = new URLSearchParams();
    params.set("page", "1");

    const year = document.getElementById("ff-year");
    const rating = document.getElementById("ff-rating");
    const series = document.getElementById("ff-series");
    const person = document.getElementById("ff-person");
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
    if (person && person.value.trim()) {
      const n = parseInt(person.value.trim(), 10);
      if (!Number.isNaN(n) && n > 0) params.set("person_id", String(n));
    }

    if (countriesRaw && countriesRaw.value.trim()) {
      countriesRaw.value
        .split(/[,;\n]+/)
        .map(function (s) {
          return s.trim();
        })
        .filter(Boolean)
        .forEach(function (c) {
          params.append("countries", c);
        });
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

    window.location.href = "/filter?" + params.toString();
  });
})();
