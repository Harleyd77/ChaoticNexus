/**
 * Motion Layer - Animation Helpers
 * Respects prefers-reduced-motion
 */

(function() {
  'use strict';

  // Check if user prefers reduced motion
  const prefersReducedMotion = () => {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  /**
   * Fade in an element
   * @param {HTMLElement} el - Element to fade in
   * @param {number} duration - Duration in ms (default 250)
   */
  function fadeIn(el, duration = 250) {
    if (!el) return Promise.resolve();
    
    if (prefersReducedMotion()) {
      el.style.opacity = '1';
      return Promise.resolve();
    }

    el.style.opacity = '0';
    el.style.transition = `opacity ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
    
    requestAnimationFrame(() => {
      el.style.opacity = '1';
    });

    return new Promise(resolve => {
      setTimeout(resolve, duration);
    });
  }

  /**
   * Fade out an element
   * @param {HTMLElement} el - Element to fade out
   * @param {number} duration - Duration in ms (default 250)
   */
  function fadeOut(el, duration = 250) {
    if (!el) return Promise.resolve();
    
    if (prefersReducedMotion()) {
      el.style.opacity = '0';
      return Promise.resolve();
    }

    el.style.transition = `opacity ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
    el.style.opacity = '0';

    return new Promise(resolve => {
      setTimeout(resolve, duration);
    });
  }

  /**
   * Expand an element (smooth height animation)
   * @param {HTMLElement} el - Element to expand
   * @param {number} duration - Duration in ms (default 350)
   */
  function expand(el, duration = 350) {
    if (!el) return Promise.resolve();
    
    if (prefersReducedMotion()) {
      el.style.display = '';
      el.style.height = 'auto';
      el.style.overflow = 'visible';
      return Promise.resolve();
    }

    // Get natural height
    el.style.display = '';
    el.style.height = 'auto';
    el.style.overflow = 'hidden';
    const height = el.scrollHeight;
    
    // Start from 0
    el.style.height = '0';
    el.style.transition = `height ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
    
    requestAnimationFrame(() => {
      el.style.height = height + 'px';
    });

    return new Promise(resolve => {
      setTimeout(() => {
        el.style.height = 'auto';
        el.style.overflow = 'visible';
        resolve();
      }, duration);
    });
  }

  /**
   * Collapse an element (smooth height animation)
   * @param {HTMLElement} el - Element to collapse
   * @param {number} duration - Duration in ms (default 350)
   */
  function collapse(el, duration = 350) {
    if (!el) return Promise.resolve();
    
    if (prefersReducedMotion()) {
      el.style.display = 'none';
      return Promise.resolve();
    }

    // Set current height explicitly
    const height = el.scrollHeight;
    el.style.height = height + 'px';
    el.style.overflow = 'hidden';
    el.style.transition = `height ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
    
    requestAnimationFrame(() => {
      el.style.height = '0';
    });

    return new Promise(resolve => {
      setTimeout(() => {
        el.style.display = 'none';
        resolve();
      }, duration);
    });
  }

  /**
   * Animate number counting up to target value
   * @param {HTMLElement} el - Element containing number
   * @param {number} toValue - Target value
   * @param {number} duration - Duration in ms (default 600)
   */
  function kpiCount(el, toValue, duration = 600) {
    if (!el) return Promise.resolve();
    
    const fromValue = parseFloat(el.textContent) || 0;
    
    if (prefersReducedMotion()) {
      el.textContent = toValue;
      return Promise.resolve();
    }

    const startTime = performance.now();
    const isDecimal = toValue % 1 !== 0;

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function (ease-out)
      const eased = 1 - Math.pow(1 - progress, 3);
      
      const current = fromValue + (toValue - fromValue) * eased;
      el.textContent = isDecimal ? current.toFixed(1) : Math.round(current);

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.textContent = isDecimal ? toValue.toFixed(1) : toValue;
      }
    }

    requestAnimationFrame(update);

    return new Promise(resolve => {
      setTimeout(resolve, duration);
    });
  }

  /**
   * Show toast notification with animation
   * @param {string} message - Message to display
   * @param {string} kind - Type: success, error, info, warning (default: success)
   * @param {number} duration - How long to show in ms (default: 3000)
   */
  function toast(message, kind = 'success', duration = 3000) {
    // Find or create toast container
    let container = document.getElementById('toast');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast';
      container.className = 'fixed bottom-4 right-4 z-50 max-w-md';
      document.body.appendChild(container);
    }

    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'polite');
    
    const bgColors = {
      success: 'bg-green-600',
      error: 'bg-red-600',
      warning: 'bg-yellow-600',
      info: 'bg-blue-600'
    };
    
    const icons = {
      success: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>',
      error: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>',
      warning: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
      info: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
    };

    toastEl.className = `${bgColors[kind] || bgColors.success} text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 mb-2 transition-all duration-300`;
    toastEl.style.opacity = '0';
    toastEl.style.transform = 'translateX(100%)';
    toastEl.innerHTML = `
      ${icons[kind] || icons.success}
      <span>${message}</span>
    `;

    container.appendChild(toastEl);

    // Animate in
    requestAnimationFrame(() => {
      toastEl.style.opacity = '1';
      toastEl.style.transform = 'translateX(0)';
    });

    // Auto-remove after duration
    setTimeout(() => {
      toastEl.style.opacity = '0';
      toastEl.style.transform = 'translateX(100%)';
      setTimeout(() => {
        toastEl.remove();
      }, 300);
    }, duration);
  }

  /**
   * Slide in from direction
   * @param {HTMLElement} el - Element to slide in
   * @param {string} from - Direction: left, right, top, bottom
   * @param {number} duration - Duration in ms (default 350)
   */
  function slideIn(el, from = 'right', duration = 350) {
    if (!el) return Promise.resolve();
    
    if (prefersReducedMotion()) {
      el.style.transform = 'none';
      el.style.opacity = '1';
      return Promise.resolve();
    }

    const transforms = {
      left: 'translateX(-100%)',
      right: 'translateX(100%)',
      top: 'translateY(-100%)',
      bottom: 'translateY(100%)'
    };

    el.style.transform = transforms[from] || transforms.right;
    el.style.opacity = '0';
    el.style.transition = `transform ${duration}ms cubic-bezier(0.4, 0, 0.2, 1), opacity ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;

    requestAnimationFrame(() => {
      el.style.transform = 'none';
      el.style.opacity = '1';
    });

    return new Promise(resolve => {
      setTimeout(resolve, duration);
    });
  }

  // Export to global scope
  window.motion = {
    fadeIn,
    fadeOut,
    expand,
    collapse,
    kpiCount,
    toast,
    slideIn,
    prefersReducedMotion
  };

  console.log('[Motion] Layer initialized. Reduced motion:', prefersReducedMotion());

})();

