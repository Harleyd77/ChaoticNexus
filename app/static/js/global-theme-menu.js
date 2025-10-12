/**
 * Lightweight controller for elements marked with data-theme-toggle.
 * Cycles through brand palettes and updates indicator/label.
 */

(function () {
  "use strict";

  const INDICATOR_COLORS = {
    dark: "#22c55e",
    light: "#f97316",
    vpc: "#38bdf8",
    "vpc-light": "#0f172a",
    chaos: "#a855f7",
    "chaos-light": "#0f172a",
  };

  function getThemeAPI() {
    if (window.themeAPI) {
      return window.themeAPI;
    }
    console.warn("[theme-menu] themeAPI missing");
    return null;
  }

  function formatLabel(theme) {
    const api = getThemeAPI();
    return api ? api.getThemeLabel(theme) : theme;
  }

  function updateButton(button) {
    const api = getThemeAPI();
    if (!api || !button) return;
    const theme = api.getTheme();
    const labelEl = button.querySelector("[data-theme-label]");
    if (labelEl) {
      labelEl.textContent = formatLabel(theme);
    } else {
      button.textContent = formatLabel(theme);
    }
    const indicator = button.querySelector("[data-theme-indicator]");
    if (indicator) {
      const color = INDICATOR_COLORS[theme] || "#22c55e";
      indicator.style.backgroundColor = color;
    }
    button.setAttribute("aria-label", `Toggle theme (current: ${formatLabel(theme)})`);
  }

  function handleClick(event) {
    event.preventDefault();
    const api = getThemeAPI();
    if (!api) return;
    api.toggleTheme();
  }

  function wireButton(button) {
    if (!button || button.dataset.themeWired) return;
    button.dataset.themeWired = "true";
    button.addEventListener("click", handleClick);
    updateButton(button);
  }

  function init() {
    document
      .querySelectorAll("[data-theme-toggle]")
      .forEach((button) => wireButton(button));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.addEventListener("themechange", () => {
    document
      .querySelectorAll("[data-theme-toggle]")
      .forEach((button) => updateButton(button));
  });
})();
