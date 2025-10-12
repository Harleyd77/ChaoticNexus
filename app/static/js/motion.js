/**
 * Motion helper utilities. Respect user motion preferences and provide
 * basic animations shared across server pages.
 */

(function () {
  "use strict";

  const prefersReducedMotion = () =>
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function fadeIn(el, duration = 250) {
    if (!el) return Promise.resolve();
    if (prefersReducedMotion()) {
      el.style.opacity = "1";
      return Promise.resolve();
    }
    el.style.opacity = "0";
    el.style.transition = `opacity ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
    requestAnimationFrame(() => {
      el.style.opacity = "1";
    });
    return new Promise((resolve) => setTimeout(resolve, duration));
  }

  function fadeOut(el, duration = 250) {
    if (!el) return Promise.resolve();
    if (prefersReducedMotion()) {
      el.style.opacity = "0";
      return Promise.resolve();
    }
    el.style.transition = `opacity ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
    el.style.opacity = "0";
    return new Promise((resolve) => setTimeout(resolve, duration));
  }

  function expand(el, duration = 350) {
    if (!el) return Promise.resolve();
    if (prefersReducedMotion()) {
      el.style.display = "";
      el.style.height = "auto";
      el.style.overflow = "visible";
      return Promise.resolve();
    }
    el.style.display = "";
    el.style.height = "auto";
    el.style.overflow = "hidden";
    const height = el.scrollHeight;
    el.style.height = "0";
    el.style.transition = `height ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
    requestAnimationFrame(() => {
      el.style.height = `${height}px`;
    });
    return new Promise((resolve) => {
      setTimeout(() => {
        el.style.height = "auto";
        el.style.overflow = "visible";
        resolve();
      }, duration);
    });
  }

  function collapse(el, duration = 350) {
    if (!el) return Promise.resolve();
    if (prefersReducedMotion()) {
      el.style.display = "none";
      return Promise.resolve();
    }
    const height = el.scrollHeight;
    el.style.height = `${height}px`;
    el.style.overflow = "hidden";
    el.style.transition = `height ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
    requestAnimationFrame(() => {
      el.style.height = "0";
    });
    return new Promise((resolve) => {
      setTimeout(() => {
        el.style.display = "none";
        resolve();
      }, duration);
    });
  }

  function kpiCount(el, toValue, duration = 600) {
    if (!el) return Promise.resolve();
    const fromValue = parseFloat(el.textContent) || 0;
    if (prefersReducedMotion()) {
      el.textContent = toValue;
      return Promise.resolve();
    }
    const start = performance.now();
    const isDecimal = toValue % 1 !== 0;

    const step = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = fromValue + (toValue - fromValue) * eased;
      el.textContent = isDecimal ? current.toFixed(1) : Math.round(current);
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = isDecimal ? toValue.toFixed(1) : toValue;
      }
    };

    requestAnimationFrame(step);
    return new Promise((resolve) => setTimeout(resolve, duration));
  }

  function ensureToastContainer() {
    let container = document.getElementById("toast");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast";
      container.className = "fixed bottom-4 right-4 z-50 max-w-md space-y-2";
      document.body.appendChild(container);
    }
    return container;
  }

  function toast(message, kind = "success", duration = 3000) {
    const container = ensureToastContainer();
    const toastEl = document.createElement("div");
    toastEl.setAttribute("role", "alert");
    toastEl.setAttribute("aria-live", "polite");

    const bgColors = {
      success: "bg-emerald-600",
      error: "bg-rose-600",
      warning: "bg-amber-500",
      info: "bg-sky-600",
    };

    toastEl.className = `${
      bgColors[kind] || bgColors.success
    } text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 transition-all duration-300`;
    toastEl.style.opacity = "0";
    toastEl.style.transform = "translateX(100%)";
    toastEl.innerHTML = `<span>${message}</span>`;
    container.appendChild(toastEl);

    requestAnimationFrame(() => {
      toastEl.style.opacity = "1";
      toastEl.style.transform = "translateX(0)";
    });

    setTimeout(() => {
      toastEl.style.opacity = "0";
      toastEl.style.transform = "translateX(100%)";
      setTimeout(() => toastEl.remove(), 300);
    }, duration);
  }

  function slideIn(el, from = "right", duration = 350) {
    if (!el) return Promise.resolve();
    if (prefersReducedMotion()) {
      el.style.transform = "none";
      el.style.opacity = "1";
      return Promise.resolve();
    }
    const transforms = {
      left: "translateX(-100%)",
      right: "translateX(100%)",
      top: "translateY(-100%)",
      bottom: "translateY(100%)",
    };
    el.style.transform = transforms[from] || transforms.right;
    el.style.opacity = "0";
    el.style.transition = `transform ${duration}ms cubic-bezier(0.4, 0, 0.2, 1), opacity ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
    requestAnimationFrame(() => {
      el.style.transform = "none";
      el.style.opacity = "1";
    });
    return new Promise((resolve) => setTimeout(resolve, duration));
  }

  window.motion = {
    fadeIn,
    fadeOut,
    expand,
    collapse,
    kpiCount,
    toast,
    slideIn,
    prefersReducedMotion,
  };

  console.log("[motion] layer ready. reduced?", prefersReducedMotion());
})();
