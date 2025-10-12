/**
 * Theme management system shared across server-rendered pages.
 * Supports dark/light plus brand palettes and keeps cookie/localStorage in sync.
 */

(function () {
  "use strict";

  const THEMES = ["dark", "light", "vpc", "vpc-light", "chaos", "chaos-light"];
  const STORAGE_KEY = "vpc_theme";
  const COOKIE_NAME = "vpc_theme";
  const DEFAULT_THEME = "dark";

  const html = document.documentElement;

  function readCookie(name) {
    return document.cookie
      .split(";")
      .map((c) => c.trim())
      .find((c) => c.startsWith(name + "="))
      ?.split("=")[1];
  }

  function writeCookie(name, value) {
    const maxAge = 365 * 24 * 60 * 60; // 1 year
    document.cookie = `${name}=${encodeURIComponent(
      value
    )}; path=/; max-age=${maxAge}; SameSite=Lax`;
  }

  function readStoredTheme() {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored && THEMES.includes(stored)) {
        return stored;
      }
    } catch (error) {
      console.warn("[theme] localStorage unavailable", error);
    }
    const cookieValue = readCookie(COOKIE_NAME);
    if (cookieValue && THEMES.includes(cookieValue)) {
      return cookieValue;
    }
    if (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: light)").matches
    ) {
      return "light";
    }
    return DEFAULT_THEME;
  }

  function setTheme(theme) {
    if (!THEMES.includes(theme)) {
      console.error("[theme] invalid theme", theme);
      return;
    }

    const previous = html.dataset.theme || DEFAULT_THEME;

    THEMES.forEach((name) => html.classList.remove(`theme-${name}`));
    if (theme !== "dark") {
      html.classList.add(`theme-${theme}`);
    }
    html.dataset.theme = theme;

    const tokenMap = {
      dark: { bg: "#0e141b", text: "#e6edf3" },
      light: { bg: "#f7f9fc", text: "#0f172a" },
      vpc: { bg: "#0B1220", text: "#E6EDF7" },
      "vpc-light": { bg: "#F7FAFF", text: "#0F172A" },
      chaos: { bg: "#0D0B12", text: "#F1EAFE" },
      "chaos-light": { bg: "#FBFAFF", text: "#0F172A" },
    };
    const tokens = tokenMap[theme] || tokenMap.dark;
    html.style.setProperty("--color-bg", tokens.bg);
    html.style.setProperty("--color-text", tokens.text);

    try {
      window.localStorage.setItem(STORAGE_KEY, theme);
    } catch (error) {
      console.warn("[theme] unable to write localStorage", error);
    }
    writeCookie(COOKIE_NAME, theme);

    window.dispatchEvent(
      new CustomEvent("themechange", { detail: { theme, previous } })
    );
  }

  function initTheme() {
    const effective = readStoredTheme();
    setTheme(effective);
    console.log("[theme] initialized", effective);
  }

  function toggleTheme() {
    const current = html.dataset.theme || DEFAULT_THEME;
    const toggleMap = {
      dark: "light",
      light: "dark",
      vpc: "vpc-light",
      "vpc-light": "vpc",
      chaos: "chaos-light",
      "chaos-light": "chaos",
    };
    setTheme(toggleMap[current] || "light");
  }

  function getThemeLabel(theme) {
    return (
      {
        dark: "Dark",
        light: "Light",
        vpc: "VPC Dark",
        "vpc-light": "VPC Light",
        chaos: "Chaotic Dark",
        "chaos-light": "Chaotic Light",
      }[theme] || theme
    );
  }

  window.themeAPI = {
    THEMES,
    initTheme,
    setTheme,
    toggleTheme,
    getThemeLabel,
    getTheme: () => html.dataset.theme || readStoredTheme(),
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTheme);
  } else {
    initTheme();
  }

  if (window.matchMedia) {
    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", (event) => {
        const stored =
          window.localStorage.getItem(STORAGE_KEY) || readCookie(COOKIE_NAME);
        if (!stored) {
          setTheme(event.matches ? "dark" : "light");
        }
      });
  }

  window.getTheme = window.themeAPI.getTheme;
  window.setTheme = window.themeAPI.setTheme;
  window.toggleTheme = window.themeAPI.toggleTheme;
})();
