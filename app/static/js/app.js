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
    const apply = () => {
      const q = (input.value || "").trim().toLowerCase();
      if (!q) {
        items.forEach((el) => (el.style.display = ""));
        return;
      }
      for (const el of items) {
        const hay = el.getAttribute("data-filter-keywords") || "";
        el.style.display = hay.includes(q) ? "" : "none";
      }
    };
    input.addEventListener("input", apply);
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
