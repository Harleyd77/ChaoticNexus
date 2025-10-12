/**
 * Common UI interactions: unsaved-form guard, loading state helpers,
 * expand/collapse controls, and utility helpers.
 */

(function () {
  "use strict";

  class UnsavedChangesGuard {
    constructor() {
      this.isDirty = false;
      this.forms = new Set();
      window.addEventListener("beforeunload", (event) => {
        if (!this.isDirty) {
          return;
        }
        event.preventDefault();
        event.returnValue =
          "You have unsaved changes. Are you sure you want to leave?";
        return event.returnValue;
      });
    }

    watch(form) {
      if (!form || this.forms.has(form)) {
        return;
      }
      this.forms.add(form);
      form.setAttribute("data-unsaved-guard", "true");
      form.addEventListener("input", () => this.setDirty(true));
      form.addEventListener("submit", () => this.setDirty(false));
    }

    unwatch(form) {
      if (!form) return;
      this.forms.delete(form);
      form.removeAttribute("data-unsaved-guard");
    }

    setDirty(flag) {
      this.isDirty = Boolean(flag);
    }

    reset() {
      this.isDirty = false;
    }
  }

  class LoadingManager {
    constructor() {
      this.active = new Set();
    }

    show(el, text = "Loading…") {
      if (!el) return;
      const id =
        el.getAttribute("data-loading-id") ||
        Math.random().toString(36).slice(2);
      el.setAttribute("data-loading-id", id);
      this.active.add(id);

      if (!el.getAttribute("data-original-content")) {
        el.setAttribute("data-original-content", el.innerHTML);
      }

      el.innerHTML = `
        <span class="inline-flex items-center gap-2">
          <span class="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-transparent"></span>
          <span>${text}</span>
        </span>`;
      el.disabled = true;
    }

    hide(el) {
      if (!el) return;
      const id = el.getAttribute("data-loading-id");
      if (id) {
        this.active.delete(id);
      }
      const original = el.getAttribute("data-original-content");
      if (original) {
        el.innerHTML = original;
        el.removeAttribute("data-original-content");
      }
      el.disabled = false;
      el.removeAttribute("data-loading-id");
    }

    isActive() {
      return this.active.size > 0;
    }
  }

  class ExpandController {
    constructor() {
      this.expanded = new Map();
    }

    toggle(triggerId, contentId) {
      if (this.expanded.get(triggerId)) {
        this.collapse(triggerId, contentId);
      } else {
        this.expand(triggerId, contentId);
      }
    }

    async expand(triggerId, contentId) {
      const trigger = document.getElementById(triggerId);
      const content = document.getElementById(contentId);
      if (!content) return;

      this.expanded.set(triggerId, true);
      if (trigger) {
        trigger.setAttribute("aria-expanded", "true");
        const chevron = trigger.querySelector("[data-chevron]");
        if (chevron) {
          chevron.style.transform = "rotate(180deg)";
        }
      }

      if (window.motion?.expand) {
        await window.motion.expand(content);
      } else {
        content.style.display = "";
      }
    }

    async collapse(triggerId, contentId) {
      const trigger = document.getElementById(triggerId);
      const content = document.getElementById(contentId);
      if (!content) return;

      this.expanded.set(triggerId, false);
      if (trigger) {
        trigger.setAttribute("aria-expanded", "false");
        const chevron = trigger.querySelector("[data-chevron]");
        if (chevron) {
          chevron.style.transform = "rotate(0deg)";
        }
      }

      if (window.motion?.collapse) {
        await window.motion.collapse(content);
      } else {
        content.style.display = "none";
      }
    }

    isExpanded(triggerId) {
      return Boolean(this.expanded.get(triggerId));
    }
  }

  function showToast(message, kind = "success", duration = 3000) {
    if (window.motion?.toast) {
      window.motion.toast(message, kind, duration);
    } else {
      window.alert(message);
    }
  }

  function confirmDialog(message, callback) {
    const accepted = window.confirm(message);
    if (accepted && typeof callback === "function") {
      callback();
    }
    return accepted;
  }

  function debounce(fn, wait = 300) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn.apply(this, args), wait);
    };
  }

  function throttle(fn, wait = 300) {
    let throttled = false;
    return function (...args) {
      if (throttled) return;
      fn.apply(this, args);
      throttled = true;
      setTimeout(() => {
        throttled = false;
      }, wait);
    };
  }

  const unsavedGuard = new UnsavedChangesGuard();
  const loadingManager = new LoadingManager();
  const expandController = new ExpandController();

  window.uiCore = {
    unsavedGuard,
    loadingManager,
    expandController,
    showToast,
    confirm: confirmDialog,
    debounce,
    throttle,
  };

  console.log("[ui-core] initialised");
})();
