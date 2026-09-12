/* =========================================================
   MPLAD AI - ANALYTICS & DASHBOARD INTERACTIONS
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* -----------------------------------------------------
       1. SIDEBAR NAVIGATION
    ----------------------------------------------------- */

    const navItems = document.querySelectorAll(".nav-item");

    navItems.forEach(item => {
        item.addEventListener("click", function () {

            navItems.forEach(nav => nav.classList.remove("active"));
            this.classList.add("active");

            const section = this.dataset.section;

            if (section) {
                showSection(section);
            }
        });
    });


    /* -----------------------------------------------------
       2. DASHBOARD SECTIONS
    ----------------------------------------------------- */

    function showSection(sectionName) {

        const sections = document.querySelectorAll(".dashboard-section");

        sections.forEach(section => {
            section.style.display = "none";
        });

        const selectedSection =
            document.getElementById(sectionName);

        if (selectedSection) {
            selectedSection.style.display = "block";
        }
    }


    /* -----------------------------------------------------
       3. FILTER FUNCTION
    ----------------------------------------------------- */

    const filterInputs =
        document.querySelectorAll(".filter-input");

    filterInputs.forEach(input => {

        input.addEventListener("input", function () {

            const searchValue =
                this.value.toLowerCase().trim();

            const rows =
                document.querySelectorAll(".project-row");

            rows.forEach(row => {

                const text =
                    row.innerText.toLowerCase();

                if (text.includes(searchValue)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }

            });
        });

    });


    /* -----------------------------------------------------
       4. PROJECT SEARCH
    ----------------------------------------------------- */

    const searchBox =
        document.getElementById("projectSearch");

    if (searchBox) {

        searchBox.addEventListener("input", function () {

            const value =
                this.value.toLowerCase();

            const projects =
                document.querySelectorAll(".project-card");

            projects.forEach(project => {

                const content =
                    project.innerText.toLowerCase();

                project.style.display =
                    content.includes(value)
                        ? ""
                        : "none";
            });
        });
    }


    /* -----------------------------------------------------
       5. RISK FILTER
    ----------------------------------------------------- */

    const riskFilter =
        document.getElementById("riskFilter");

    if (riskFilter) {

        riskFilter.addEventListener("change", function () {

            const selectedRisk =
                this.value.toLowerCase();

            const rows =
                document.querySelectorAll(".project-row");

            rows.forEach(row => {

                const risk =
                    row.dataset.risk
                        ? row.dataset.risk.toLowerCase()
                        : "";

                if (
                    selectedRisk === "all" ||
                    risk === selectedRisk
                ) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }

            });
        });
    }


    /* -----------------------------------------------------
       6. STATUS FILTER
    ----------------------------------------------------- */

    const statusFilter =
        document.getElementById("statusFilter");

    if (statusFilter) {

        statusFilter.addEventListener("change", function () {

            const selectedStatus =
                this.value.toLowerCase();

            const rows =
                document.querySelectorAll(".project-row");

            rows.forEach(row => {

                const status =
                    row.dataset.status
                        ? row.dataset.status.toLowerCase()
                        : "";

                if (
                    selectedStatus === "all" ||
                    status === selectedStatus
                ) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }

            });
        });
    }


    /* -----------------------------------------------------
       7. PROJECT DETAIL MODAL
    ----------------------------------------------------- */

    const projectButtons =
        document.querySelectorAll(".view-project");

    const modal =
        document.getElementById("projectModal");

    const closeModal =
        document.getElementById("closeModal");

    projectButtons.forEach(button => {

        button.addEventListener("click", function () {

            const projectId =
                this.dataset.projectId;

            const projectName =
                this.dataset.projectName;

            const projectStatus =
                this.dataset.status;

            const projectRisk =
                this.dataset.risk;

            const projectCost =
                this.dataset.cost;

            const elements = {
                id: document.getElementById("modalProjectId"),
                name: document.getElementById("modalProjectName"),
                status: document.getElementById("modalProjectStatus"),
                risk: document.getElementById("modalProjectRisk"),
                cost: document.getElementById("modalProjectCost")
            };

            if (elements.id)
                elements.id.textContent = projectId || "N/A";

            if (elements.name)
                elements.name.textContent = projectName || "Project";

            if (elements.status)
                elements.status.textContent = projectStatus || "N/A";

            if (elements.risk)
                elements.risk.textContent = projectRisk || "Low";

            if (elements.cost)
                elements.cost.textContent = projectCost || "₹0";

            if (modal) {
                modal.classList.add("show");
            }
        });

    });


    if (closeModal) {

        closeModal.addEventListener("click", () => {

            if (modal) {
                modal.classList.remove("show");
            }

        });

    }


    window.addEventListener("click", event => {

        if (event.target === modal) {
            modal.classList.remove("show");
        }

    });


    /* -----------------------------------------------------
       8. ALERT DETAILS
    ----------------------------------------------------- */

    const alertCards =
        document.querySelectorAll(".alert-card");

    alertCards.forEach(card => {

        card.addEventListener("click", function () {

            const message =
                this.dataset.message;

            if (message) {
                alert(message);
            }

        });

    });


    /* -----------------------------------------------------
       9. EXPORT REPORT
    ----------------------------------------------------- */

    const exportButton =
        document.getElementById("exportReport");

    if (exportButton) {

        exportButton.addEventListener("click", () => {

            const rows =
                document.querySelectorAll(".project-row");

            if (rows.length === 0) {
                alert("No project data available.");
                return;
            }

            let csv = [];

            csv.push(
                "Project,Status,Risk Score,Risk Level,Estimated Cost"
            );

            rows.forEach(row => {

                const cells =
                    row.querySelectorAll("td");

                if (cells.length >= 5) {

                    const data = [];

                    cells.forEach(cell => {

                        data.push(
                            `"${cell.innerText
                                .replace(/"/g, '""')
                                .trim()}"`
                        );

                    });

                    csv.push(data.join(","));
                }
            });

            const blob =
                new Blob(
                    [csv.join("\n")],
                    { type: "text/csv;charset=utf-8;" }
                );

            const url =
                URL.createObjectURL(blob);

            const link =
                document.createElement("a");

            link.href = url;

            link.download =
                "MPLAD_Project_Analytics.csv";

            document.body.appendChild(link);

            link.click();

            document.body.removeChild(link);

            URL.revokeObjectURL(url);
        });

    }


    /* -----------------------------------------------------
       10. REFRESH DASHBOARD
    ----------------------------------------------------- */

    const refreshButton =
        document.getElementById("refreshDashboard");

    if (refreshButton) {

        refreshButton.addEventListener("click", () => {

            refreshButton.classList.add("loading");

            setTimeout(() => {

                window.location.reload();

            }, 700);

        });

    }


    /* -----------------------------------------------------
       11. RISK SCORE COLOR
    ----------------------------------------------------- */

    function updateRiskColors() {

        const riskElements =
            document.querySelectorAll(".risk-score");

        riskElements.forEach(element => {

            const score =
                parseFloat(
                    element.innerText.replace("%", "")
                );

            if (isNaN(score)) return;

            element.classList.remove(
                "risk-low",
                "risk-medium",
                "risk-high",
                "risk-critical"
            );

            if (score >= 85) {

                element.classList.add(
                    "risk-critical"
                );

            } else if (score >= 65) {

                element.classList.add(
                    "risk-high"
                );

            } else if (score >= 40) {

                element.classList.add(
                    "risk-medium"
                );

            } else {

                element.classList.add(
                    "risk-low"
                );
            }

        });
    }

    updateRiskColors();


    /* -----------------------------------------------------
       12. ANIMATED KPI COUNTERS
    ----------------------------------------------------- */

    function animateCounter(element) {

        const target =
            parseFloat(
                element.dataset.value
            );

        if (isNaN(target)) return;

        let current = 0;

        const duration = 1000;

        const startTime = performance.now();

        function update(currentTime) {

            const progress =
                Math.min(
                    (currentTime - startTime) / duration,
                    1
                );

            current =
                Math.floor(
                    progress * target
                );

            element.textContent =
                current.toLocaleString("en-IN");

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    }


    document
        .querySelectorAll(".kpi-number")
        .forEach(animateCounter);


    /* -----------------------------------------------------
       13. PROGRESS BARS
    ----------------------------------------------------- */

    const progressBars =
        document.querySelectorAll(".progress-fill");

    progressBars.forEach(bar => {

        const value =
            bar.dataset.progress || 0;

        setTimeout(() => {

            bar.style.width =
                `${Math.min(value, 100)}%`;

        }, 200);

    });


    /* -----------------------------------------------------
       14. TOOLTIP
    ----------------------------------------------------- */

    const tooltipElements =
        document.querySelectorAll("[data-tooltip]");

    tooltipElements.forEach(element => {

        element.addEventListener("mouseenter", () => {

            const tooltip =
                document.createElement("div");

            tooltip.className =
                "analytics-tooltip";

            tooltip.textContent =
                element.dataset.tooltip;

            document.body.appendChild(tooltip);

            const rect =
                element.getBoundingClientRect();

            tooltip.style.left =
                `${rect.left + window.scrollX}px`;

            tooltip.style.top =
                `${rect.bottom + window.scrollY + 8}px`;

            element._tooltip = tooltip;
        });


        element.addEventListener("mouseleave", () => {

            if (element._tooltip) {

                element._tooltip.remove();

                element._tooltip = null;
            }

        });

    });


    /* -----------------------------------------------------
       15. TABLE ROW SELECTION
    ----------------------------------------------------- */

    const tableRows =
        document.querySelectorAll(
            ".project-row"
        );

    tableRows.forEach(row => {

        row.addEventListener("click", function () {

            tableRows.forEach(r => {
                r.classList.remove("selected");
            });

            this.classList.add("selected");
        });

    });


    /* -----------------------------------------------------
       16. AI ANALYSIS BUTTON
    ----------------------------------------------------- */

    const analyzeButton =
        document.getElementById("runAnalysis");

    if (analyzeButton) {

        analyzeButton.addEventListener("click", async () => {

            const originalText =
                analyzeButton.innerHTML;

            analyzeButton.disabled = true;

            analyzeButton.innerHTML =
                "Analyzing...";

            try {

                /*
                 * Flask API endpoint.
                 * Change this endpoint only if your
                 * app.py uses another route.
                 */

                const response =
                    await fetch("/api/analyze", {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            action: "risk_analysis"
                        })
                    });


                if (!response.ok) {
                    throw new Error(
                        "Analysis request failed"
                    );
                }


                const data =
                    await response.json();


                if (data.success) {

                    alert(
                        "AI risk analysis completed successfully."
                    );

                    /*
                     * Reload dashboard so that
                     * newly calculated values appear.
                     */

                    window.location.reload();

                } else {

                    alert(
                        data.message ||
                        "Analysis could not be completed."
                    );
                }


            } catch (error) {

                console.error(
                    "AI Analysis Error:",
                    error
                );

                alert(
                    "Unable to connect to the AI analysis service."
                );

            } finally {

                analyzeButton.disabled = false;

                analyzeButton.innerHTML =
                    originalText;
            }

        });

    }


    /* -----------------------------------------------------
       17. NAVIGATION TO PROJECT PAGE
    ----------------------------------------------------- */

    const projectLinks =
        document.querySelectorAll(
            "[data-project-link]"
        );

    projectLinks.forEach(link => {

        link.addEventListener("click", function () {

            const projectId =
                this.dataset.projectLink;

            if (projectId) {

                window.location.href =
                    `/project/${encodeURIComponent(projectId)}`;
            }

        });

    });


    /* -----------------------------------------------------
       18. MOBILE SIDEBAR
    ----------------------------------------------------- */

    const menuButton =
        document.getElementById("menuButton");

    const sidebar =
        document.querySelector(".sidebar");

    if (menuButton && sidebar) {

        menuButton.addEventListener("click", () => {

            sidebar.classList.toggle("mobile-open");

        });

    }


    /* -----------------------------------------------------
       19. CLOSE MOBILE SIDEBAR
    ----------------------------------------------------- */

    document.addEventListener("click", event => {

        if (
            sidebar &&
            sidebar.classList.contains("mobile-open") &&
            !sidebar.contains(event.target) &&
            event.target !== menuButton
        ) {

            sidebar.classList.remove(
                "mobile-open"
            );
        }

    });


    /* -----------------------------------------------------
       20. DASHBOARD INITIALIZATION
    ----------------------------------------------------- */

    console.log(
        "MPLAD Analytics Dashboard initialized successfully."
    );

});