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

  function init() {
    initPendingRouteNotices();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
