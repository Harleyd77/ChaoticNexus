// Global behaviours shared across server-rendered templates.

(function () {
  "use strict";

  function handlePendingRoute(event) {
    event.preventDefault();
    const target = event.currentTarget.getAttribute("data-pending-target");
    const message = target
      ? `The route ${target} is still being migrated from the legacy app.`
      : "This feature is still being migrated from the legacy app.";
    if (window.uiCore?.showToast) {
      window.uiCore.showToast(message, "info", 3500);
    } else {
      window.alert(message);
    }
  }

  function initPendingRouteNotices() {
    document
      .querySelectorAll("[data-pending-route]")
      .forEach((el) => el.addEventListener("click", handlePendingRoute, false));
  }

  function initJobsListFiltering() {
    const container = document.getElementById("jobs-list");
    if (!container) return;

    const scope = container.querySelector('[data-filter-scope="job-cards"]');
    if (!scope) return;

    const input = document.querySelector('form[role="search"] input[name="q"]');
    if (!input) return;

    const items = Array.from(scope.querySelectorAll('[data-filter-keywords]'));
    if (!items.length) return;

    const emptyState = container.querySelector("[data-filter-empty]");
    const countEl = container.querySelector("[data-filter-count]");
    const totalEl = container.querySelector("[data-filter-total]");

    if (totalEl) {
      totalEl.textContent = items.length.toString();
    }

    const apply = () => {
      const rawQuery = (input.value || "").trim().toLowerCase();
      const needles = rawQuery.split(/\s+/).filter(Boolean);
      let visible = 0;

      for (const el of items) {
        const hay = (el.dataset.filterKeywords || el.getAttribute("data-filter-keywords") || "").toLowerCase();
        const matches = needles.length
          ? needles.every((needle) => hay.includes(needle))
          : true;

        el.hidden = !matches;
        if (matches) {
          visible += 1;
        }
      }

      if (countEl) {
        countEl.textContent = visible.toString();
      }
      if (emptyState) {
        emptyState.hidden = visible !== 0;
      }
      container.dataset.filterActive = needles.length ? "true" : "false";
    };

    input.addEventListener("input", apply, { passive: true });
    input.addEventListener("change", apply, { passive: true });
    apply();
  }

  function init() {
    initPendingRouteNotices();
    initJobsListFiltering();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
