/**
 * Форма RandomParams: сбор query string и переход на GET /random
 */
(function () {
  const form = document.getElementById("random-filters-form");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const params = new URLSearchParams();

    const year = document.getElementById("rf-year");
    const rating = document.getElementById("rf-rating");
    const series = document.getElementById("rf-series");
    const countriesRaw = document.getElementById("rf-countries");
    const genresSelect = document.getElementById("rf-genres");
    const typesSelect = document.getElementById("rf-types");
    const genresAdv = document.getElementById("rf-genres-adv");
    const typesAdv = document.getElementById("rf-types-adv");

    if (year && year.value.trim()) params.set("year", year.value.trim());
    if (rating && rating.value.trim()) params.set("rating", rating.value.trim());
    if (series && (series.value === "true" || series.value === "false")) {
      params.set("is_series", series.value);
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

    window.location.href = "/random?" + params.toString();
  });
})();
