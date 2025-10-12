/**
 * Lightweight client-side interactions for the Jobs Kanban view.
 * Provides local drag-and-drop and status toasts until APIs are migrated.
 */

(function () {
  "use strict";

  const dropzones = document.querySelectorAll("[data-kanban-dropzone]");
  const cards = document.querySelectorAll("[data-kanban-card]");

  if (!dropzones.length || !cards.length) {
    return;
  }

  const columnLabel = (zone) => {
    const section = zone.closest("[data-kanban-column]");
    return section?.dataset.kanbanLabel || "Unknown";
  };

  const showToast = (message, kind = "info") => {
    if (window.uiCore?.showToast) {
      window.uiCore.showToast(message, kind, 2600);
    } else {
      console.log("[kanban]", message);
    }
  };

  const refreshCounts = () => {
    dropzones.forEach((zone) => {
      const key = zone.dataset.kanbanDropzone;
      const count = zone.querySelectorAll("[data-kanban-card]").length;
      const counter = document.querySelector(`[data-kanban-count="${key}"]`);
      if (counter) {
        counter.textContent = count;
      }
      const emptyState = zone.querySelector(`[data-kanban-empty="${key}"]`);
      if (emptyState) {
        emptyState.hidden = count > 0;
      }
    });
  };

  let draggedCard = null;

  cards.forEach((card) => {
    card.addEventListener("dragstart", (event) => {
      draggedCard = card;
      card.classList.add("opacity-60");
      event.dataTransfer.setData("text/plain", card.dataset.jobId || "");
      event.dataTransfer.effectAllowed = "move";
    });

    card.addEventListener("dragend", () => {
      card.classList.remove("opacity-60");
      draggedCard = null;
    });
  });

  dropzones.forEach((zone) => {
    zone.addEventListener("dragover", (event) => {
      event.preventDefault();
      zone.classList.add("ring-2", "ring-slate-500/60");
      event.dataTransfer.dropEffect = "move";
    });

    zone.addEventListener("dragleave", () => {
      zone.classList.remove("ring-2", "ring-slate-500/60");
    });

    zone.addEventListener("drop", (event) => {
      event.preventDefault();
      zone.classList.remove("ring-2", "ring-slate-500/60");

      const jobId =
        event.dataTransfer.getData("text/plain") ||
        draggedCard?.dataset.jobId ||
        "";
      if (!jobId) {
        return;
      }
      const card =
        document.querySelector(`[data-kanban-card][data-job-id="${jobId}"]`) ||
        draggedCard;
      if (!card) {
        return;
      }

      zone.appendChild(card);
      card.dataset.department = zone.dataset.kanbanDropzone || "";
      refreshCounts();
      showToast(`Moved job #${jobId} to ${columnLabel(zone)}`, "info");
    });
  });

  document.querySelectorAll("[data-kanban-status]").forEach((button) => {
    button.addEventListener("click", () => {
      const jobId = button.dataset.jobId;
      showToast(
        `Status update for job #${jobId} will be available once the API is migrated.`,
        "warning",
      );
    });
  });

  refreshCounts();
})();
