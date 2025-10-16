/* Calendar range picker logic for intake forms.
 * Updates paired hidden inputs (startSelector, endSelector) with ISO dates.
 */

(function () {
  "use strict";

  const DAY_MS = 24 * 60 * 60 * 1000;

  function toISO(date) {
    return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 10);
  }

  function fromISO(value) {
    if (!value) return null;
    const parts = value.split("-");
    if (parts.length !== 3) return null;
    const date = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    return isNaN(date.getTime()) ? null : date;
  }

  function startOfMonth(date) {
    return new Date(date.getFullYear(), date.getMonth(), 1);
  }

  function addMonths(date, count) {
    return new Date(date.getFullYear(), date.getMonth() + count, 1);
  }

  function daysInMonth(date) {
    const start = startOfMonth(date);
    const next = addMonths(start, 1);
    return Math.round((next - start) / DAY_MS);
  }

  function getMonthMatrix(viewDate) {
    const firstDay = startOfMonth(viewDate);
    const offset = (firstDay.getDay() + 7) % 7; // Sunday start
    const total = daysInMonth(viewDate);
    const matrix = [];
    let current = new Date(firstDay.getFullYear(), firstDay.getMonth(), 1 - offset);
    for (let i = 0; i < 42; i += 1) {
      matrix.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }
    return matrix;
  }

  function formatMonthTitle(date, locale) {
    return date.toLocaleDateString(locale || undefined, {
      month: "long",
      year: "numeric",
    });
  }

  function isSameDay(a, b) {
    return (
      a &&
      b &&
      a.getFullYear() === b.getFullYear() &&
      a.getMonth() === b.getMonth() &&
      a.getDate() === b.getDate()
    );
  }

  function withinRange(date, start, end) {
    if (!start || !end) return false;
    const time = date.setHours(0, 0, 0, 0);
    return time >= start.setHours(0, 0, 0, 0) && time <= end.setHours(0, 0, 0, 0);
  }

  function bindCalendar(root) {
    const startInput = document.querySelector(root.dataset.startSelector);
    const endInput = document.querySelector(root.dataset.endSelector);
    if (!startInput || !endInput) return;

    const locale = root.dataset.locale || undefined;
    const today = new Date();
    let startDate = fromISO(startInput.value) || today;
    let endDate = fromISO(endInput.value) || new Date(today.getTime() + 7 * DAY_MS);
    if (startDate > endDate) {
      [startDate, endDate] = [endDate, startDate];
    }

    let viewDate = startOfMonth(startDate);

    function render() {
      const theme = document.documentElement.dataset.theme || "dark";
      root.setAttribute("data-theme", theme);

      const titleEl = root.querySelector(".cal-title");
      if (titleEl) titleEl.textContent = formatMonthTitle(viewDate, locale);

      const daysContainer = root.querySelector(".cal-days");
      if (!daysContainer) return;

      daysContainer.innerHTML = "";
      const matrix = getMonthMatrix(viewDate);
      matrix.forEach((date) => {
        const button = document.createElement("button");
        button.className = "cal-day";
        button.type = "button";
        button.textContent = String(date.getDate());

        if (date.getMonth() !== viewDate.getMonth()) {
          button.classList.add("cal-empty", "is-muted");
          button.disabled = true;
        }

        if (isSameDay(date, startDate)) {
          button.classList.add("is-selected", "is-range-start");
        }
        if (isSameDay(date, endDate)) {
          button.classList.add("is-selected", "is-range-end");
        }
        if (!isSameDay(date, startDate) && !isSameDay(date, endDate) && withinRange(new Date(date), new Date(startDate), new Date(endDate))) {
          button.classList.add("is-in-range");
        }

        button.addEventListener("click", () => {
          const clicked = new Date(date);
          if (!startDate || (startDate && endDate)) {
            startDate = clicked;
            endDate = null;
          } else if (clicked < startDate) {
            endDate = startDate;
            startDate = clicked;
          } else {
            endDate = clicked;
          }

          startInput.value = startDate ? toISO(startDate) : "";
          endInput.value = endDate ? toISO(endDate) : "";

          if (startInput.dispatchEvent) startInput.dispatchEvent(new Event("change", { bubbles: true }));
          if (endInput.dispatchEvent) endInput.dispatchEvent(new Event("change", { bubbles: true }));

          render();
          root.dispatchEvent(new CustomEvent("calendar-update", {
            detail: { start: startInput.value, end: endInput.value },
          }));
        });

        daysContainer.appendChild(button);
      });

      const summaryRange = root.querySelector(".cal-summary-range");
      if (summaryRange) {
        summaryRange.textContent = startDate
          ? endDate
            ? `${startInput.value} → ${endInput.value}`
            : `${startInput.value} → …`
          : "Select a start date";
      }
    }

    root.querySelector("[data-cal-prev]")?.addEventListener("click", () => {
      viewDate = addMonths(viewDate, -1);
      render();
    });
    root.querySelector("[data-cal-next]")?.addEventListener("click", () => {
      viewDate = addMonths(viewDate, 1);
      render();
    });
    root.querySelector("[data-cal-today]")?.addEventListener("click", () => {
      const now = new Date();
      startDate = now;
      endDate = new Date(now.getTime() + 7 * DAY_MS);
      startInput.value = toISO(startDate);
      endInput.value = toISO(endDate);
      viewDate = startOfMonth(now);
      render();
      root.dispatchEvent(
        new CustomEvent("calendar-update", {
          detail: { start: startInput.value, end: endInput.value },
        })
      );
    });

    root.querySelector("[data-cal-close]")?.addEventListener("click", () => {
      root.classList.add("hidden");
    });

    render();

    window.addEventListener("themechange", () => render());
  }

  function initCalendars() {
    document
      .querySelectorAll("[data-calendar-range]")
      .forEach((root) => bindCalendar(root));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCalendars);
  } else {
    initCalendars();
  }
})();

