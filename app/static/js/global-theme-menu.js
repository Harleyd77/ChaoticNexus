/**
 * Lightweight controller for theme selector dropdown and toggle buttons.
 * Handles both data-theme-selector (dropdown) and data-theme-toggle (button).
 */

(function () {
  "use strict";

  const INDICATOR_COLORS = {
    dark: "#22c55e",
    light: "#f97316",
    forge: "#ff8c42",
    ocean: "#06b6d4",
    sunset: "#f472b6",
    forest: "#10b981",
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

  // === Dropdown Selector Handling ===
  function applyThemeToSelect(select, theme) {
    if (!select) return;
    let matched = false;
    Array.from(select.options).forEach((option) => {
      const isMatch = option.value === theme;
      option.selected = isMatch;
      if (isMatch) {
        matched = true;
      }
    });
    if (matched) {
      select.value = theme;
    }
    select.setAttribute("data-selected-theme", theme);

    const labelTarget = select.dataset.themeLabelTarget;
    if (labelTarget) {
      const labelEl = document.querySelector(labelTarget);
      if (labelEl) {
        labelEl.textContent = formatLabel(theme);
      }
    }
  }

  function updateSelector(select) {
    const api = getThemeAPI();
    if (!api || !select) return;
    const theme = api.getTheme();
    applyThemeToSelect(select, theme);
  }

  function handleSelectorChange(event) {
    const api = getThemeAPI();
    if (!api) return;
    const selectedTheme = event.target.value;
    api.setTheme(selectedTheme);
    applyThemeToSelect(event.target, selectedTheme);
  }

  function wireSelector(select) {
    if (!select || select.dataset.themeWired) return;
    select.dataset.themeWired = "true";
    select.addEventListener("change", handleSelectorChange);
    updateSelector(select);
  }

  // === Button Toggle Handling (for backwards compatibility) ===
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

  // === Initialization ===
  function refreshSelectors() {
    document
      .querySelectorAll("[data-theme-selector]")
      .forEach((select) => updateSelector(select));
  }

  function refreshButtons() {
    document
      .querySelectorAll("[data-theme-toggle]")
      .forEach((button) => updateButton(button));
  }

  function refreshThemeControls() {
    refreshSelectors();
    refreshButtons();
  }

  function init() {
    document
      .querySelectorAll("[data-theme-selector]")
      .forEach((select) => wireSelector(select));

    document
      .querySelectorAll("[data-theme-toggle]")
      .forEach((button) => wireButton(button));

    refreshThemeControls();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }

  window.addEventListener("themechange", refreshThemeControls);
})();
