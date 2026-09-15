let allRecords = [];
let filteredRecords = [];


/* =====================================================
   INIT
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    initializeDashboard
);


async function initializeDashboard() {

    try {

        const response = await fetch(
            "/api/risk-analysis?source=synthetic"
        );

        if (!response.ok) {
            throw new Error(
                `API returned ${response.status}`
            );
        }

        const result = await response.json();

        /*
         * Your Flask API returns:
         *
         * {
         *     data: [...]
         * }
         */

        allRecords =
            Array.isArray(result.data)
                ? result.data
                : [];

        filteredRecords =
            [...allRecords];


        console.log(
            "MPLADS SENTINEL records:",
            allRecords.length
        );


        populateFilters();

        renderDashboard();

        initializeCharts(
            filteredRecords
        );

        initializeMap(
            filteredRecords
        );


        updateLastUpdated();


    } catch (error) {

        console.error(
            "Command Center failed:",
            error
        );

        showDashboardError();

    }

}


/* =====================================================
   FILTERS
===================================================== */

function populateFilters() {

    populateSelect(
        "fyFilter",
        [
            "financial_year",
            "fy",
            "financialYear"
        ]
    );


    populateSelect(
        "stateFilter",
        [
            "state",
            "State"
        ]
    );


    populateSelect(
        "categoryFilter",
        [
            "work_category",
            "category",
            "Work Category"
        ]
    );


    document
        .getElementById("fyFilter")
        .addEventListener(
            "change",
            applyFilters
        );


    document
        .getElementById("stateFilter")
        .addEventListener(
            "change",
            applyFilters
        );


    document
        .getElementById("categoryFilter")
        .addEventListener(
            "change",
            applyFilters
        );

}


function populateSelect(
    id,
    possibleFields
) {

    const select =
        document.getElementById(id);


    if (!select) return;


    const values =
        uniqueValues(
            allRecords,
            possibleFields
        );


    values.forEach(value => {

        const option =
            document.createElement("option");

        option.value = value;

        option.textContent = value;

        select.appendChild(option);

    });

}


function applyFilters() {

    const fy =
        document.getElementById(
            "fyFilter"
        ).value;


    const state =
        document.getElementById(
            "stateFilter"
        ).value;


    const category =
        document.getElementById(
            "categoryFilter"
        ).value;


    filteredRecords =
        allRecords.filter(row => {

            const rowFY =
                getValue(
                    row,
                    [
                        "financial_year",
                        "fy",
                        "financialYear"
                    ]
                );


            const rowState =
                getValue(
                    row,
                    [
                        "state",
                        "State"
                    ]
                );


            const rowCategory =
                getValue(
                    row,
                    [
                        "work_category",
                        "category",
                        "Work Category"
                    ]
                );


            if (
                fy !== "all" &&
                String(rowFY) !== fy
            ) {
                return false;
            }


            if (
                state !== "all" &&
                String(rowState) !== state
            ) {
                return false;
            }


            if (
                category !== "all" &&
                String(rowCategory) !== category
            ) {
                return false;
            }


            return true;

        });


    renderDashboard();


    initializeCharts(
        filteredRecords
    );


    initializeMap(
        filteredRecords
    );

}


/* =====================================================
   DASHBOARD
===================================================== */

function renderDashboard() {

    updateKPIs();

    updateRiskOverview();

    updateRiskIntelligence();

    updateStateRanking();

    updatePriorityAlerts();

    updateAIInsight();

}


/* =====================================================
   KPI
===================================================== */

function updateKPIs() {

    const total =
        filteredRecords.length;


    const highRisk =
        filteredRecords.filter(
            row =>
                riskLevel(row) === "HIGH"
        ).length;


    const delayed =
        filteredRecords.filter(
            row =>
                numericValue(
                    row,
                    ["delay_days"]
                ) > 30
        ).length;


    const mlAnomalies =
        filteredRecords.filter(
            row =>
                isMLAnomaly(row)
        ).length;


    const sanctioned =
        sumField(
            filteredRecords,
            [
                "sanction_amount",
                "sanctioned_amount",
                "cost_estimate_lakhs"
            ]
        );


    setText(
        "totalWorks",
        formatNumber(total)
    );


    setText(
        "highRisk",
        formatNumber(highRisk)
    );


    setText(
        "delayedWorks",
        formatNumber(delayed)
    );


    setText(
        "mlAnomalies",
        formatNumber(mlAnomalies)
    );


    if (sanctioned === null) {

        setText(
            "totalSanctioned",
            "—"
        );

    } else {

        setText(
            "totalSanctioned",
            formatLakhs(sanctioned)
        );

    }

}


/* =====================================================
   RISK OVERVIEW
===================================================== */

function updateRiskOverview() {

    const high =
        filteredRecords.filter(
            row =>
                riskLevel(row) === "HIGH"
        ).length;


    const medium =
        filteredRecords.filter(
            row =>
                riskLevel(row) === "MEDIUM"
        ).length;


    const low =
        filteredRecords.filter(
            row =>
                riskLevel(row) === "LOW"
        ).length;


    setText(
        "riskTotal",
        formatNumber(
            filteredRecords.length
        )
    );


    setText(
        "riskHigh",
        formatNumber(high)
    );


    setText(
        "riskMedium",
        formatNumber(medium)
    );


    setText(
        "riskLow",
        formatNumber(low)
    );

}


/* =====================================================
   INTELLIGENCE
===================================================== */

function updateRiskIntelligence() {

    const high =
        filteredRecords.filter(
            row =>
                riskLevel(row) === "HIGH"
        ).length;


    const delayed =
        filteredRecords.filter(
            row =>
                numericValue(
                    row,
                    ["delay_days"]
                ) > 30
        ).length;


    const ml =
        filteredRecords.filter(
            row =>
                isMLAnomaly(row)
        ).length;


    const low =
        filteredRecords.filter(
            row =>
                riskLevel(row) === "LOW"
        ).length;


    setText(
        "intelHigh",
        formatNumber(high)
    );


    setText(
        "intelDelay",
        formatNumber(delayed)
    );


    setText(
        "intelML",
        formatNumber(ml)
    );


    const lowText =
        document.getElementById(
            "intelLowText"
        );


    if (lowText) {

        lowText.innerHTML =
            `<strong>${formatNumber(low)}</strong>
             works remain within the low-risk tier.`;

    }

}


/* =====================================================
   STATE RANKING
===================================================== */

function updateStateRanking() {

    const container =
        document.getElementById(
            "stateList"
        );


    if (!container) return;


    const stateMap = {};


    filteredRecords.forEach(row => {

        const state =
            getValue(
                row,
                [
                    "state",
                    "State"
                ]
            );


        if (!state) return;


        if (!stateMap[state]) {

            stateMap[state] = {
                works: 0,
                high: 0,
                medium: 0,
                sanctioned: 0
            };

        }


        stateMap[state].works++;


        const risk =
            riskLevel(row);


        if (risk === "HIGH") {

            stateMap[state].high++;

        }


        if (risk === "MEDIUM") {

            stateMap[state].medium++;

        }


        const amount =
            numericValue(
                row,
                [
                    "sanction_amount",
                    "sanctioned_amount"
                ]
            );


        if (amount !== null) {

            stateMap[state].sanctioned +=
                amount;

        }

    });


    const states =
        Object.entries(stateMap)
            .sort(
                (a, b) =>
                    b[1].high -
                    a[1].high
            )
            .slice(0, 6);


    if (!states.length) {

        container.innerHTML = `
            <div class="loading">
                State information unavailable
                in the current dataset.
            </div>
        `;

        return;

    }


    container.innerHTML =
        states.map(
            ([state, info]) => {

                const riskColor =
                    info.high > 0
                        ? "red"
                        : info.medium > 0
                            ? "orange"
                            : "green";


                return `

                    <div class="state-item">

                        <span
                            class="state-dot"
                            style="
                                background:
                                var(--${riskColor});
                            ">
                        </span>


                        <div class="state-info">

                            <strong>
                                ${escapeHTML(state)}
                            </strong>

                            <span>
                                ${formatNumber(info.works)}
                                works
                                ${
                                    info.sanctioned
                                    ? " · " +
                                      formatLakhs(
                                          info.sanctioned
                                      )
                                    : ""
                                }
                            </span>

                        </div>


                        <div class="state-risk-count">

                            <strong>
                                ${formatNumber(info.high)}
                            </strong>

                            <span>
                                high-risk
                            </span>

                        </div>

                    </div>

                `;

            }
        )
        .join("");

}


/* =====================================================
   PRIORITY ALERTS
===================================================== */

function updatePriorityAlerts() {

    const table =
        document.getElementById(
            "alertsTable"
        );


    if (!table) return;


    const alerts =
        [...filteredRecords]
            .filter(
                row =>
                    riskLevel(row) === "HIGH"
            )
            .sort(
                (a, b) =>
                    numericValue(
                        b,
                        ["hybrid_risk_score"]
                    ) -
                    numericValue(
                        a,
                        ["hybrid_risk_score"]
                    )
            )
            .slice(0, 8);


    if (!alerts.length) {

        table.innerHTML = `
            <tr>
                <td colspan="7"
                    class="loading">
                    No high-risk works found
                    in the available dataset.
                </td>
            </tr>
        `;

        return;

    }


    table.innerHTML =
        alerts.map(
            row => {

                const id =
                    getValue(
                        row,
                        [
                            "record_id",
                            "work_id",
                            "id"
                        ]
                    ) || "—";


                const state =
                    getValue(
                        row,
                        [
                            "state",
                            "State"
                        ]
                    ) || "";


                const district =
                    getValue(
                        row,
                        [
                            "district",
                            "District"
                        ]
                    ) || "";


                const category =
                    getValue(
                        row,
                        [
                            "work_category",
                            "category"
                        ]
                    ) || "—";


                const score =
                    numericValue(
                        row,
                        ["hybrid_risk_score"]
                    );


                const reason =
                    getPrimarySignal(row);


                const status =
                    getValue(
                        row,
                        ["status"]
                    ) || "—";


                return `

                    <tr>

                        <td>
                            <strong>
                                ${escapeHTML(id)}
                            </strong>
                        </td>


                        <td>
                            ${escapeHTML(
                                district
                            )}

                            ${
                                district && state
                                ? ", "
                                : ""
                            }

                            ${escapeHTML(state)}
                        </td>


                        <td>
                            ${escapeHTML(
                                category
                            )}
                        </td>


                        <td>

                            <span
                                class="
                                risk-badge
                                high
                                ">
                                HIGH
                            </span>

                        </td>


                        <td>
                            ${escapeHTML(
                                reason
                            )}
                        </td>


                        <td>

                            <span class="status-text">
                                ${escapeHTML(
                                    status
                                )}
                            </span>

                        </td>


                        <td>

                            <a
                                class="action-link"
                                href="/project/${encodeURIComponent(id)}">
                                Investigate →
                            </a>

                        </td>

                    </tr>

                `;

            }
        )
        .join("");

}


/* =====================================================
   AI INSIGHT
===================================================== */

function updateAIInsight() {

    const element =
        document.getElementById(
            "aiInsight"
        );


    if (!element) return;


    const total =
        filteredRecords.length;


    if (!total) {

        element.textContent =
            "No records are available for analysis.";

        return;

    }


    const high =
        filteredRecords.filter(
            row =>
                riskLevel(row) === "HIGH"
        ).length;


    const medium =
        filteredRecords.filter(
            row =>
                riskLevel(row) === "MEDIUM"
        ).length;


    const delayed =
        filteredRecords.filter(
            row =>
                numericValue(
                    row,
                    ["delay_days"]
                ) > 30
        ).length;


    const ml =
        filteredRecords.filter(
            row =>
                isMLAnomaly(row)
        ).length;


    const signals = [];


    if (high > 0) {

        signals.push(
            `${formatNumber(high)} high-risk works`
        );

    }


    if (delayed > 0) {

        signals.push(
            `${formatNumber(delayed)} delayed works`
        );

    }


    if (ml > 0) {

        signals.push(
            `${formatNumber(ml)} ML anomaly signals`
        );

    }


    if (!signals.length) {

        element.textContent =
            `The current dataset contains ${
                formatNumber(total)
            } analyzed works. No priority risk signal was identified by the configured rules and ML model.`;

        return;

    }


    element.textContent =
        `The current dataset contains ${
            formatNumber(total)
        } analyzed works. Detected signals include ${
            signals.join(", ")
        }. These signals should be treated as investigation priorities rather than proof of misconduct.`;

}


/* =====================================================
   SEARCH
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const search =
            document.getElementById(
                "globalSearch"
            );


        if (!search) return;


        search.addEventListener(
            "input",
            () => {

                const query =
                    search.value
                        .trim()
                        .toLowerCase();


                if (!query) {

                    filteredRecords =
                        [...allRecords];

                } else {

                    filteredRecords =
                        allRecords.filter(
                            row =>
                                JSON.stringify(row)
                                    .toLowerCase()
                                    .includes(query)
                        );

                }


                renderDashboard();


                initializeCharts(
                    filteredRecords
                );


                initializeMap(
                    filteredRecords
                );

            }
        );

    }
);


/* =====================================================
   HELPERS
===================================================== */

function riskLevel(row) {

    const value =
        getValue(
            row,
            [
                "hybrid_risk_level",
                "risk_level"
            ]
        );


    return String(
        value || "LOW"
    ).toUpperCase();

}


function isMLAnomaly(row) {

    const value =
        getValue(
            row,
            [
                "ml_anomaly",
                "is_anomaly"
            ]
        );


    if (
        value === true ||
        value === 1 ||
        value === "1" ||
        String(value).toLowerCase() === "true"
    ) {

        return true;

    }


    return false;

}


function getPrimarySignal(row) {

    const reasons =
        getValue(
            row,
            [
                "hybrid_risk_reasons",
                "rule_reasons"
            ]
        );


    if (Array.isArray(reasons)) {

        return reasons[0] || "Risk signal";

    }


    if (reasons) {

        return String(reasons)
            .split(",")[0]
            .trim();

    }


    if (
        Number(
            getValue(
                row,
                ["cost_overrun_amount"]
            )
        ) > 0
    ) {

        return "Cost anomaly";

    }


    if (
        Number(
            getValue(
                row,
                ["delay_days"]
            )
        ) > 30
    ) {

        return "Timeline delay";

    }


    if (isMLAnomaly(row)) {

        return "ML anomaly";

    }


    return "Risk anomaly";

}


function getValue(
    row,
    keys
) {

    for (
        const key of keys
    ) {

        if (
            row[key] !== undefined &&
            row[key] !== null &&
            row[key] !== ""
        ) {

            return row[key];

        }

    }

    return null;

}


function numericValue(
    row,
    keys
) {

    const value =
        getValue(
            row,
            keys
        );


    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        return null;

    }


    const number =
        Number(value);


    return Number.isFinite(number)
        ? number
        : null;

}


function sumField(
    records,
    keys
) {

    let total = 0;

    let found = false;


    records.forEach(row => {

        const value =
            numericValue(
                row,
                keys
            );


        if (value !== null) {

            total += value;

            found = true;

        }

    });


    return found
        ? total
        : null;

}


function uniqueValues(
    records,
    keys
) {

    const values = [];


    records.forEach(row => {

        const value =
            getValue(
                row,
                keys
            );


        if (
            value !== null &&
            value !== undefined &&
            String(value).trim() !== ""
        ) {

            values.push(
                String(value)
            );

        }

    });


    return [
        ...new Set(values)
    ].sort();

}


function formatNumber(
    value
) {

    return Number(value || 0)
        .toLocaleString(
            "en-IN"
        );

}


function formatLakhs(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "—";

    }


    const number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {

        return "—";

    }


    return "₹" +
        number.toLocaleString(
            "en-IN",
            {
                maximumFractionDigits: 1
            }
        ) +
        " L";

}


function setText(
    id,
    value
) {

    const element =
        document.getElementById(id);


    if (element) {

        element.textContent =
            value;

    }

}


function escapeHTML(
    value
) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


function updateLastUpdated() {

    const element =
        document.getElementById(
            "lastUpdated"
        );


    if (!element) return;


    const now =
        new Date();


    element.textContent =
        now.toLocaleString(
            "en-IN",
            {
                day: "2-digit",
                month: "short",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            }
        );

}


function showDashboardError() {

    [
        "totalWorks",
        "totalSanctioned",
        "highRisk",
        "delayedWorks",
        "mlAnomalies",
        "riskTotal",
        "riskHigh",
        "riskMedium",
        "riskLow",
        "intelHigh",
        "intelDelay",
        "intelML"
    ].forEach(
        id =>
            setText(id, "—")
    );


    const alerts =
        document.getElementById(
            "alertsTable"
        );


    if (alerts) {

        alerts.innerHTML = `
            <tr>
                <td colspan="7"
                    class="loading">
                    Unable to load risk-analysis data.
                </td>
            </tr>
        `;

    }

}


/* expose for charts/map */

window.getSentinelRecords =
    () => filteredRecords;