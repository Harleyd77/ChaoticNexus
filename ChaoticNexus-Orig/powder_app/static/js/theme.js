/**
 * Theme Management System
 * Supports: dark, light, vpc, vpc-light, chaos, chaos-light
 * Persists via localStorage, emits 'themechange' event
 */

(function() {
  'use strict';

  const THEMES = ['dark', 'light', 'vpc', 'vpc-light', 'chaos', 'chaos-light'];
  const STORAGE_KEY = 'vpc_theme';
  const DEFAULT_THEME = 'dark';

  /**
   * Get current theme from localStorage or system preference
   */
  function getTheme() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored && THEMES.includes(stored)) {
        return stored;
      }
    } catch (e) {
      console.warn('[Theme] localStorage not available:', e);
    }

    // Fallback to system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      return 'light';
    }

    return DEFAULT_THEME;
  }

  /**
   * Set theme and persist to localStorage
   * @param {string} theme - One of: dark, light, vpc, vpc-light, chaos, chaos-light
   */
  function setTheme(theme) {
    if (!THEMES.includes(theme)) {
      console.error('[Theme] Invalid theme:', theme);
      return;
    }

    const html = document.documentElement;
    
    // Remove all theme classes
    THEMES.forEach(t => {
      html.classList.remove(`theme-${t}`);
    });

    // Add new theme class (except 'dark' which is default)
    if (theme !== 'dark') {
      html.classList.add(`theme-${theme}`);
    }

    // Set data attribute for easier targeting
    html.setAttribute('data-theme', theme);

    // Update background immediately to avoid flash
    const bgColors = {
      'dark': '#0e141b',
      'light': '#f7f9fc',
      'vpc': '#0B1220',
      'vpc-light': '#F7FAFF',
      'chaos': '#0D0B12',
      'chaos-light': '#FBFAFF'
    };
    html.style.backgroundColor = bgColors[theme] || bgColors.dark;

    // Persist to localStorage
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {
      console.warn('[Theme] Could not save to localStorage:', e);
    }

    // Emit custom event for listeners
    window.dispatchEvent(new CustomEvent('themechange', {
      detail: { theme, previous: getTheme() }
    }));

    console.log('[Theme] Switched to:', theme);
  }

  /**
   * Initialize theme on page load
   */
  function initTheme() {
    const theme = getTheme();
    setTheme(theme);
    console.log('[Theme] Initialized:', theme);
  }

  /**
   * Toggle between dark and light variants of current brand
   */
  function toggleTheme() {
    const current = getTheme();
    const toggleMap = {
      'dark': 'light',
      'light': 'dark',
      'vpc': 'vpc-light',
      'vpc-light': 'vpc',
      'chaos': 'chaos-light',
      'chaos-light': 'chaos'
    };
    setTheme(toggleMap[current] || 'light');
  }

  /**
   * Get theme label for display
   */
  function getThemeLabel(theme) {
    const labels = {
      'dark': 'Dark',
      'light': 'Light',
      'vpc': 'VPC Dark',
      'vpc-light': 'VPC Light',
      'chaos': 'Chaotic Dark',
      'chaos-light': 'Chaotic Light'
    };
    return labels[theme] || theme;
  }

  // Export to global scope
  window.themeAPI = {
    getTheme,
    setTheme,
    initTheme,
    toggleTheme,
    getThemeLabel,
    THEMES
  };

  // Auto-init on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
  } else {
    initTheme();
  }

  // Listen for system preference changes
  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      const current = getTheme();
      // Only auto-switch if user hasn't set a preference
      if (!localStorage.getItem(STORAGE_KEY)) {
        setTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

})();

// Legacy compat (old code may call these directly)
window.getTheme = window.themeAPI.getTheme;
window.setTheme = window.themeAPI.setTheme;
window.toggleTheme = window.themeAPI.toggleTheme;

