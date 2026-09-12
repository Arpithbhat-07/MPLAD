/* =====================================================
   MPLAD AI MONITORING - MAIN INTERACTIVE SCRIPT
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* -------------------------------------------------
       1. LIVE SEARCH ON PROJECT TABLE
    ------------------------------------------------- */
    const projectSearchInput = document.getElementById("projectSearch");
    const clearSearchBtn = document.getElementById("clearSearchBtn");
    const projectTable = document.getElementById("projectTable");

    function executeLiveSearch() {
        if (!projectSearchInput || !projectTable) return;

        const filter = projectSearchInput.value.toLowerCase().trim();
        const rows = projectTable.querySelectorAll("tbody tr");
        let visibleCount = 0;

        if (clearSearchBtn) {
            clearSearchBtn.style.display = filter.length > 0 ? "block" : "none";
        }

        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            const matches = text.includes(filter);
            row.style.display = matches ? "" : "none";
            if (matches) visibleCount++;
        });

        // Update live count indicator if present
        const countDisplay = document.getElementById("filteredCount");
        if (countDisplay) {
            countDisplay.innerText = visibleCount;
        }
    }

    if (projectSearchInput) {
        projectSearchInput.addEventListener("input", executeLiveSearch);
        projectSearchInput.addEventListener("keyup", function (e) {
            if (e.key === "Escape") {
                clearSearch();
            }
        });
    }

    if (clearSearchBtn) {
        clearSearchBtn.addEventListener("click", clearSearch);
    }

    /* -------------------------------------------------
       2. CLICKABLE TABLE ROWS
    ------------------------------------------------- */
    const clickableRows = document.querySelectorAll(".table-wrapper table tbody tr");
    clickableRows.forEach(row => {
        row.addEventListener("click", function (event) {
            // Ignore click if user clicked an explicit link or button inside the row
            if (event.target.tagName.toLowerCase() === "a" || event.target.tagName.toLowerCase() === "button" || event.target.closest("a") || event.target.closest("button")) {
                return;
            }
            const link = this.querySelector(".project-link") || this.querySelector(".table-action-btn");
            if (link && link.href) {
                window.location.href = link.href;
            }
        });
    });

    /* -------------------------------------------------
       3. BUTTON CLICK MICRO-ANIMATION
    ------------------------------------------------- */
    document.querySelectorAll("button, .primary-button, .outline-button, .filter-button, .page-btn").forEach(button => {
        button.addEventListener("click", function () {
            this.style.transform = "scale(0.98)";
            setTimeout(() => {
                this.style.transform = "scale(1)";
            }, 100);
        });
    });

    /* -------------------------------------------------
       4. MODAL EVENT LISTENERS
    ------------------------------------------------- */
    document.querySelectorAll(".modal-backdrop").forEach(backdrop => {
        backdrop.addEventListener("click", function (event) {
            if (event.target === this) {
                this.classList.remove("active");
            }
        });
    });

    document.querySelectorAll(".modal-close-btn, .modal-close-trigger").forEach(btn => {
        btn.addEventListener("click", function () {
            const modal = this.closest(".modal-backdrop");
            if (modal) {
                modal.classList.remove("active");
            }
        });
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            document.querySelectorAll(".modal-backdrop.active").forEach(modal => {
                modal.classList.remove("active");
            });
        }
    });

    /* -------------------------------------------------
       5. PROGRESS BAR LOAD ANIMATION
    ------------------------------------------------- */
    const progressBars = document.querySelectorAll(".bar span, .progress-line span, .big-progress span");
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width;
        if (targetWidth) {
            bar.style.width = "0%";
            setTimeout(() => {
                bar.style.transition = "width 0.8s ease-out";
                bar.style.width = targetWidth;
            }, 100);
        }
    });

});

/* =====================================================
   GLOBAL HELPER FUNCTIONS
===================================================== */

function clearSearch() {
    const input = document.getElementById("projectSearch");
    const clearBtn = document.getElementById("clearSearchBtn");
    if (input) {
        input.value = "";
        if (clearBtn) clearBtn.style.display = "none";
        const rows = document.querySelectorAll("#projectTable tbody tr");
        rows.forEach(row => {
            row.style.display = "";
        });
        const countDisplay = document.getElementById("filteredCount");
        if (countDisplay) {
            countDisplay.innerText = rows.length;
        }
    }
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add("active");
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove("active");
    }
}

function showNotification(message, type = "info") {
    const existingToast = document.querySelector(".toast-notification");
    if (existingToast) existingToast.remove();

    const toast = document.createElement("div");
    toast.className = "toast-notification";
    if (type === "success") {
        toast.style.background = "#159957";
    } else if (type === "danger") {
        toast.style.background = "#d9534f";
    } else {
        toast.style.background = "#0c2f52";
    }

    const icon = type === "success" ? "✓ " : (type === "danger" ? "⚠ " : "ℹ ");
    toast.innerText = icon + message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = "opacity 0.4s, transform 0.4s";
        toast.style.opacity = "0";
        toast.style.transform = "translateY(15px)";
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}