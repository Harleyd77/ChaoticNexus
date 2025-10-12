/**
 * MCP/Chrome DevTools Self-Test Script
 * Only runs when ?mcp_check=1 query parameter is present
 * Logs structured [MCP-*] markers to console
 * Sets window.__MCP_RESULTS__ object with pass/fail counts
 */

(function() {
  'use strict';

  // Only run if mcp_check=1 parameter is present
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('mcp_check') !== '1') {
    return; // Exit early
  }

  console.log('[MCP-START] Running diagnostics...');

  const results = {
    passed: 0,
    failed: 0,
    tests: []
  };

  /**
   * Run a test and log result
   */
  function test(name, fn) {
    try {
      const result = fn();
      if (result) {
        console.log(`[MCP-OK] ${name}`);
        results.passed++;
        results.tests.push({ name, status: 'pass' });
      } else {
        console.error(`[MCP-ERR] ${name}: returned false`);
        results.failed++;
        results.tests.push({ name, status: 'fail', error: 'returned false' });
      }
    } catch (error) {
      console.error(`[MCP-ERR] ${name}:`, error);
      results.failed++;
      results.tests.push({ name, status: 'fail', error: error.message });
    }
  }

  /**
   * Async test wrapper
   */
  async function testAsync(name, fn) {
    try {
      const result = await fn();
      if (result) {
        console.log(`[MCP-OK] ${name}`);
        results.passed++;
        results.tests.push({ name, status: 'pass' });
      } else {
        console.error(`[MCP-ERR] ${name}: returned false`);
        results.failed++;
        results.tests.push({ name, status: 'fail', error: 'returned false' });
      }
    } catch (error) {
      console.error(`[MCP-ERR] ${name}:`, error);
      results.failed++;
      results.tests.push({ name, status: 'fail', error: error.message });
    }
  }

  /**
   * Wait for DOM ready
   */
  function ready(fn) {
    if (document.readyState !== 'loading') {
      fn();
    } else {
      document.addEventListener('DOMContentLoaded', fn);
    }
  }

  /**
   * Run all tests
   */
  ready(async () => {
    // === Basic Presence Tests ===
    test('customer-card exists', () => {
      return document.querySelector('[data-testid="customer-card"]') !== null;
    });

    test('expand-card exists', () => {
      return document.querySelector('[data-testid="expand-card"]') !== null;
    });

    test('view-more exists', () => {
      return document.querySelector('[data-testid="view-more"]') !== null;
    });

    test('theme-menu exists', () => {
      return document.querySelector('[data-testid="theme-menu"]') !== null;
    });

    // === Theme System Tests ===
    test('themeAPI is available', () => {
      return typeof window.themeAPI !== 'undefined';
    });

    test('current theme is set on html element', () => {
      const html = document.documentElement;
      return html.hasAttribute('data-theme');
    });

    test('theme persists to localStorage', () => {
      return localStorage.getItem('vpc_theme') !== null;
    });

    // Test theme switching
    await testAsync('theme switching works', async () => {
      if (!window.themeAPI) return false;
      
      const originalTheme = window.themeAPI.getTheme();
      
      // Switch to different theme
      const testTheme = originalTheme === 'dark' ? 'light' : 'dark';
      window.themeAPI.setTheme(testTheme);
      
      // Wait a bit
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Check if theme changed
      const currentTheme = window.themeAPI.getTheme();
      const htmlClass = document.documentElement.getAttribute('data-theme');
      
      // Restore original
      window.themeAPI.setTheme(originalTheme);
      
      return currentTheme === testTheme && htmlClass === testTheme;
    });

    // === Motion Layer Tests ===
    test('motion API is available', () => {
      return typeof window.motion !== 'undefined';
    });

    test('motion.expand function exists', () => {
      return typeof window.motion.expand === 'function';
    });

    test('motion.collapse function exists', () => {
      return typeof window.motion.collapse === 'function';
    });

    test('motion.kpiCount function exists', () => {
      return typeof window.motion.kpiCount === 'function';
    });

    test('motion.toast function exists', () => {
      return typeof window.motion.toast === 'function';
    });

    // === UI Core Tests ===
    test('uiCore API is available', () => {
      return typeof window.uiCore !== 'undefined';
    });

    test('unsavedGuard is available', () => {
      return typeof window.uiCore.unsavedGuard !== 'undefined';
    });

    test('loadingManager is available', () => {
      return typeof window.uiCore.loadingManager !== 'undefined';
    });

    // === Expandable Card Test ===
    await testAsync('expanding card reveals dashboard', async () => {
      const expandBtn = document.querySelector('[data-testid="expand-card"]');
      if (!expandBtn) return false;

      // Click expand
      expandBtn.click();

      // Wait for animation
      await new Promise(resolve => setTimeout(resolve, 500));

      // Check if dashboard is visible
      const kpi = document.querySelector('[data-testid="kpi-active"]');
      const table = document.querySelector('[data-testid="recent-jobs-table"]');

      return kpi !== null || table !== null;
    });

    // === KPI Value Tests ===
    test('KPI values are numeric or null', () => {
      const kpis = document.querySelectorAll('[data-testid^="kpi-"]');
      if (kpis.length === 0) return true; // Skip if not on page

      for (const kpi of kpis) {
        const text = kpi.textContent.trim();
        if (text && text !== '—' && text !== 'N/A') {
          const num = parseFloat(text);
          if (isNaN(num)) {
            console.warn('[MCP-WARN] KPI value is not numeric:', text);
            return false;
          }
        }
      }
      return true;
    });

    // === Accessibility Tests ===
    test('customer cards are keyboard focusable', () => {
      const cards = document.querySelectorAll('[data-testid="customer-card"]');
      if (cards.length === 0) return true; // Skip if not on page

      for (const card of cards) {
        if (card.getAttribute('tabindex') === null && !card.matches('a, button')) {
          return false;
        }
      }
      return true;
    });

    test('expand buttons have aria-expanded', () => {
      const expandBtns = document.querySelectorAll('[data-testid="expand-card"]');
      if (expandBtns.length === 0) return true; // Skip if not on page

      for (const btn of expandBtns) {
        if (!btn.hasAttribute('aria-expanded')) {
          return false;
        }
      }
      return true;
    });

    // === Final Summary ===
    console.log(`[MCP-END] passed:${results.passed} failed:${results.failed}`);
    console.log('[MCP-RESULTS]', JSON.stringify(results, null, 2));

    // Expose results to window for external inspection
    window.__MCP_RESULTS__ = results;

    // Visual indicator in console
    if (results.failed === 0) {
      console.log('%c✓ All MCP checks passed!', 'color: #22c55e; font-weight: bold; font-size: 16px;');
    } else {
      console.log('%c✗ Some MCP checks failed', 'color: #ef4444; font-weight: bold; font-size: 16px;');
    }
  });

})();

