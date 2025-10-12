/**
 * UI Core - Common UI Interactions
 * Expand/collapse, unsaved changes guard, loading states
 */

(function() {
  'use strict';

  /**
   * Unsaved Changes Guard
   * Warns user when navigating away with unsaved form changes
   */
  class UnsavedChangesGuard {
    constructor() {
      this.isDirty = false;
      this.forms = new Set();
      this.init();
    }

    init() {
      // Listen for beforeunload
      window.addEventListener('beforeunload', (e) => {
        if (this.isDirty) {
          e.preventDefault();
          e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
          return e.returnValue;
        }
      });
    }

    /**
     * Register a form for tracking
     */
    watch(formEl) {
      if (!formEl) return;
      
      this.forms.add(formEl);
      formEl.setAttribute('data-watched', 'true');

      // Track input changes
      formEl.addEventListener('input', () => {
        this.setDirty(true);
      });

      // Reset on submit
      formEl.addEventListener('submit', () => {
        this.setDirty(false);
      });
    }

    /**
     * Unregister a form
     */
    unwatch(formEl) {
      if (!formEl) return;
      this.forms.delete(formEl);
      formEl.removeAttribute('data-watched');
    }

    /**
     * Set dirty state
     */
    setDirty(dirty) {
      this.isDirty = dirty;
      console.log('[UnsavedGuard] Dirty:', dirty);
    }

    /**
     * Reset all forms
     */
    reset() {
      this.isDirty = false;
      console.log('[UnsavedGuard] Reset');
    }
  }

  /**
   * Loading State Manager
   * Show/hide loading indicators
   */
  class LoadingManager {
    constructor() {
      this.active = new Set();
    }

    /**
     * Show loading state on element
     */
    show(el, text = 'Loading...') {
      if (!el) return;

      const id = el.getAttribute('data-loading-id') || Math.random().toString(36);
      el.setAttribute('data-loading-id', id);
      this.active.add(id);

      // Store original content
      if (!el.getAttribute('data-original-content')) {
        el.setAttribute('data-original-content', el.innerHTML);
      }

      // Show loading spinner
      el.innerHTML = `
        <span class="inline-flex items-center gap-2">
          <span class="loading-spinner"></span>
          <span>${text}</span>
        </span>
      `;
      el.disabled = true;
    }

    /**
     * Hide loading state
     */
    hide(el) {
      if (!el) return;

      const id = el.getAttribute('data-loading-id');
      if (id) {
        this.active.delete(id);
      }

      // Restore original content
      const original = el.getAttribute('data-original-content');
      if (original) {
        el.innerHTML = original;
        el.removeAttribute('data-original-content');
      }

      el.disabled = false;
      el.removeAttribute('data-loading-id');
    }

    /**
     * Check if any loading is active
     */
    isActive() {
      return this.active.size > 0;
    }
  }

  /**
   * Expand/Collapse Controller
   * Manages expandable sections with smooth animations
   */
  class ExpandController {
    constructor() {
      this.expanded = new Map();
    }

    /**
     * Toggle expand/collapse
     */
    toggle(triggerId, contentId) {
      const isExpanded = this.expanded.get(triggerId);
      
      if (isExpanded) {
        this.collapse(triggerId, contentId);
      } else {
        this.expand(triggerId, contentId);
      }
    }

    /**
     * Expand a section
     */
    async expand(triggerId, contentId) {
      const trigger = document.getElementById(triggerId);
      const content = document.getElementById(contentId);
      
      if (!content) return;

      this.expanded.set(triggerId, true);

      // Update trigger state
      if (trigger) {
        trigger.setAttribute('aria-expanded', 'true');
        const chevron = trigger.querySelector('[data-chevron]');
        if (chevron) {
          chevron.style.transform = 'rotate(180deg)';
        }
      }

      // Animate content
      if (window.motion) {
        await window.motion.expand(content);
      } else {
        content.style.display = '';
      }
    }

    /**
     * Collapse a section
     */
    async collapse(triggerId, contentId) {
      const trigger = document.getElementById(triggerId);
      const content = document.getElementById(contentId);
      
      if (!content) return;

      this.expanded.set(triggerId, false);

      // Update trigger state
      if (trigger) {
        trigger.setAttribute('aria-expanded', 'false');
        const chevron = trigger.querySelector('[data-chevron]');
        if (chevron) {
          chevron.style.transform = 'rotate(0deg)';
        }
      }

      // Animate content
      if (window.motion) {
        await window.motion.collapse(content);
      } else {
        content.style.display = 'none';
      }
    }

    /**
     * Check if expanded
     */
    isExpanded(triggerId) {
      return this.expanded.get(triggerId) || false;
    }
  }

  /**
   * Toast Notification Helper
   * Simple wrapper around motion.toast
   */
  function showToast(message, kind = 'success', duration = 3000) {
    if (window.motion && window.motion.toast) {
      window.motion.toast(message, kind, duration);
    } else {
      // Fallback: use alert
      alert(message);
    }
  }

  /**
   * Confirm Dialog Helper
   * Shows a native confirm dialog
   */
  function confirm(message, callback) {
    if (window.confirm(message)) {
      if (typeof callback === 'function') {
        callback();
      }
      return true;
    }
    return false;
  }

  /**
   * Debounce Helper
   * Delays function execution until after wait period
   */
  function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  /**
   * Throttle Helper
   * Ensures function is called at most once per wait period
   */
  function throttle(func, wait = 300) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, wait);
      }
    };
  }

  // Create global instances
  const unsavedGuard = new UnsavedChangesGuard();
  const loadingManager = new LoadingManager();
  const expandController = new ExpandController();

  // Export to global scope
  window.uiCore = {
    unsavedGuard,
    loadingManager,
    expandController,
    showToast,
    confirm,
    debounce,
    throttle
  };

  console.log('[UI-Core] Initialized');

})();

