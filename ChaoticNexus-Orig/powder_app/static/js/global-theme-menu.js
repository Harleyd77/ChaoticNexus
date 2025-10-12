/**
 * Global Theme Menu
 * Automatically injects theme selector into all pages
 * Place in header/topbar area
 */

(function() {
  'use strict';

  // Wait for DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    // Don't inject if already exists
    if (document.querySelector('[data-global-theme-menu]')) return;

    // Create theme menu HTML - integrate with existing layouts
    const menu = document.createElement('div');
    menu.setAttribute('data-global-theme-menu', 'true');
    menu.style.cssText = 'position: relative; display: inline-block;';
    menu.innerHTML = `
      <style>
        @media (max-width: 640px) {
          #globalThemeBtn {
            min-width: 100px !important;
            padding: 4px 8px !important;
            font-size: 11px !important;
          }
          #globalThemeBtn svg {
            width: 14px !important;
            height: 14px !important;
          }
        }
        @media (max-width: 480px) {
          #globalThemeBtn {
            min-width: 40px !important;
            width: 40px !important;
            padding: 6px !important;
            justify-content: center !important;
          }
          #globalThemeBtn span:last-child {
            display: none !important;
          }
          #globalThemeBtn svg:last-child {
            display: none !important;
          }
        }
      </style>
      <button id="globalThemeBtn" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px; border-radius: 8px; background: #1a2533; color: #d9e7ff; border: 1px solid var(--border, #1f2a37); cursor: pointer; text-decoration: none; font-size: 12px; min-width: 120px; max-width: 140px; justify-content: space-between; transition: all 0.2s ease; box-shadow: 0 2px 8px rgba(0,0,0,0.15); white-space: nowrap; flex-shrink: 0;">
        <span style="display: flex; align-items: center; gap: 6px;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="4"/>
            <path d="M12 2v2m0 16v2m10-10h-2M4 12H2m15.364-7.364-1.414 1.414M8.05 16.95l-1.414 1.414m12.728 0-1.414-1.414M8.05 7.05 6.636 5.636"/>
          </svg>
          <span id="globalThemeLabel">Dark</span>
        </span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="transition: transform 0.2s ease;">
          <path d="M19 9l-7 7-7-7"/>
        </svg>
      </button>
      <div id="globalThemeDropdown" style="position: absolute; top: 100%; right: 0; margin-top: 8px; background: var(--panel, #111923); border-radius: 12px; box-shadow: 0 12px 40px rgba(0,0,0,0.35); overflow: hidden; border: 1px solid var(--border, #1f2a37); min-width: 200px; z-index: 10000; display: none;">
        <div style="padding: 8px;">
          <button data-theme="dark" class="theme-option" style="width: 100%; text-align: left; padding: 8px 12px; border-radius: 8px; background: transparent; color: var(--text, #e6edf3); border: none; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 8px; transition: background 0.2s ease; margin-bottom: 2px;">
            🌙 <span>Dark</span>
          </button>
          <button data-theme="light" class="theme-option" style="width: 100%; text-align: left; padding: 8px 12px; border-radius: 8px; background: transparent; color: var(--text, #e6edf3); border: none; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 8px; transition: background 0.2s ease; margin-bottom: 2px;">
            ☀️ <span>Light</span>
          </button>
          <hr style="border: none; border-top: 1px solid var(--border, #1f2a37); margin: 4px 0;">
          <button data-theme="vpc" class="theme-option" style="width: 100%; text-align: left; padding: 8px 12px; border-radius: 8px; background: transparent; color: var(--text, #e6edf3); border: none; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 8px; transition: background 0.2s ease; margin-bottom: 2px;">
            🔷 <span>VPC Dark</span>
          </button>
          <button data-theme="vpc-light" class="theme-option" style="width: 100%; text-align: left; padding: 8px 12px; border-radius: 8px; background: transparent; color: var(--text, #e6edf3); border: none; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 8px; transition: background 0.2s ease; margin-bottom: 2px;">
            💎 <span>VPC Light</span>
          </button>
          <hr style="border: none; border-top: 1px solid var(--border, #1f2a37); margin: 4px 0;">
          <button data-theme="chaos" class="theme-option" style="width: 100%; text-align: left; padding: 8px 12px; border-radius: 8px; background: transparent; color: var(--text, #e6edf3); border: none; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 8px; transition: background 0.2s ease; margin-bottom: 2px;">
            ⚡ <span>Chaotic Dark</span>
          </button>
          <button data-theme="chaos-light" class="theme-option" style="width: 100%; text-align: left; padding: 8px 12px; border-radius: 8px; background: transparent; color: var(--text, #e6edf3); border: none; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 8px; transition: background 0.2s ease; margin-bottom: 2px;">
            ✨ <span>Chaotic Light</span>
          </button>
        </div>
      </div>
    `;

    // Find the best place to inject the theme menu
    let targetContainer = null;
    
    // Try to find common header/toolbar containers
    const selectors = [
      '.topbar-inner',           // customers page
      '.topbar .actions',        // customers page actions area
      '.topbar-inner > div:last-child', // nav page header right side
      '.topbar > div:last-child', // nav page header right side
      'header > div:last-child', // general header right side
      '.header-actions',         // common header actions class
      '.toolbar',                // toolbar areas
      'header'                   // any header
    ];
    
    for (const selector of selectors) {
      const container = document.querySelector(selector);
      if (container) {
        // Check if this container already has flex layout
        const computedStyle = window.getComputedStyle(container);
        if (computedStyle.display === 'flex' || container.style.display === 'flex') {
          targetContainer = container;
          break;
        }
      }
    }
    
    if (targetContainer) {
      targetContainer.appendChild(menu);
      console.log('[ThemeMenu] Injected into flex container:', targetContainer.className || targetContainer.tagName);
    } else {
      // Fallback: append to body with fixed position
      menu.style.cssText = 'position: fixed; top: 72px; right: 20px; z-index: 9999;';
      document.body.appendChild(menu);
      console.log('[ThemeMenu] Injected as fixed position fallback');
    }

    // Add hover effects
    const btn = menu.querySelector('#globalThemeBtn');
    if (btn) {
      btn.addEventListener('mouseenter', () => {
        btn.style.borderColor = 'var(--accent, #3b82f6)';
      });
      btn.addEventListener('mouseleave', () => {
        btn.style.borderColor = 'var(--border, #1f2a37)';
      });
    }

    // Set up event listeners
    setupListeners();
  }

  function setupListeners() {
    const btn = document.getElementById('globalThemeBtn');
    const dropdown = document.getElementById('globalThemeDropdown');
    const label = document.getElementById('globalThemeLabel');

    if (!btn || !dropdown || !label) return;

    // Toggle dropdown
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isHidden = dropdown.style.display === 'none';
      dropdown.style.display = isHidden ? 'block' : 'none';
      
      // Rotate arrow to show dropdown state
      const arrow = btn.querySelector('svg:last-child');
      if (arrow) {
        arrow.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
      }
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!e.target.closest('[data-global-theme-menu]')) {
        dropdown.style.display = 'none';
        // Reset arrow rotation
        const arrow = btn.querySelector('svg:last-child');
        if (arrow) {
          arrow.style.transform = 'rotate(0deg)';
        }
      }
    });

    // Theme option clicks and hover effects
    const options = dropdown.querySelectorAll('[data-theme]');
    options.forEach(option => {
      // Add hover effects
      option.addEventListener('mouseenter', () => {
        if (!option.style.background.includes('var(--hover')) {
          option.style.background = 'var(--hover, #172235)';
        }
      });
      option.addEventListener('mouseleave', () => {
        if (!option.style.background.includes('var(--hover')) {
          option.style.background = 'transparent';
        }
      });
      
      // Handle clicks
      option.addEventListener('click', () => {
        const theme = option.getAttribute('data-theme');
        if (window.themeAPI) {
          window.themeAPI.setTheme(theme);
        } else if (window.setTheme) {
          window.setTheme(theme);
        }
        dropdown.style.display = 'none';
        // Reset arrow rotation
        const arrow = btn.querySelector('svg:last-child');
        if (arrow) {
          arrow.style.transform = 'rotate(0deg)';
        }
      });
    });

    // Update label on theme change
    function updateLabel() {
      const theme = window.themeAPI ? window.themeAPI.getTheme() : (window.getTheme ? window.getTheme() : 'dark');
      const labels = {
        'dark': 'Dark',
        'light': 'Light',
        'vpc': 'VPC Dark',
        'vpc-light': 'VPC Light',
        'chaos': 'Chaotic Dark',
        'chaos-light': 'Chaotic Light'
      };
      label.textContent = labels[theme] || theme;

      // Highlight active option
      options.forEach(opt => {
        if (opt.getAttribute('data-theme') === theme) {
          opt.style.background = 'var(--hover, #172235)';
          opt.style.color = 'var(--accent, #3b82f6)';
        } else {
          opt.style.background = 'transparent';
          opt.style.color = 'var(--text, #e6edf3)';
        }
      });
    }

    // Listen for theme changes
    window.addEventListener('themechange', updateLabel);

    // Initial update
    setTimeout(updateLabel, 100);
  }

})();

