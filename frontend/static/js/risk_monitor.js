/* =========================================================
   MPLADS SENTINEL — RISK MONITOR
========================================================= */

let allRiskRecords = [];

let filteredRiskRecords = [];

let currentPage = 1;

const PAGE_SIZE = 12;

let currentSortField = "hybrid_risk_score";

let currentSortDirection = "desc";


/* =========================================================
   INITIALIZE
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initializeRiskMonitor
);


async function initializeRiskMonitor() {

    bindControls();

    await loadRiskData();

}


/* =========================================================
   API
========================================================= */

async function loadRiskData() {

    const table =
        document.getElementById(
            "riskTableBody"
        );


    try {

        table.innerHTML = `
            <tr>
                <td colspan="10"
                    class="table-loading">
                    Loading risk intelligence...
                </td>
            </tr>
        `;


        const response =
            await fetch(
                "/api/risk-analysis?source=synthetic"
            );


        if (!response.ok) {

            throw new Error(
                `API error ${response.status}`
            );

        }


        const result =
            await response.json();


        allRiskRecords =
            Array.isArray(result.data)
                ? result.data
                : [];


        console.log(
            "Risk Monitor records:",
            allRiskRecords.length
        );


        populateFilters();


        applyFilters();


        updateSidebarTime();


    } catch (error) {

        console.error(
            "Risk Monitor error:",
            error
        );


        table.innerHTML = `
            <tr>
                <td colspan="10"
                    class="table-loading">
                    Unable to load risk-analysis data.
                </td>
            </tr>
        `;


        setMatchCount(0);

    }

}


/* =========================================================
   CONTROLS
========================================================= */

function bindControls() {


    document
        .getElementById("workSearch")
        .addEventListener(
            "input",
            resetAndFilter
        );


    document
        .getElementById("stateFilter")
        .addEventListener(
            "change",
            resetAndFilter
        );


    document
        .getElementById("districtFilter")
        .addEventListener(
            "change",
            resetAndFilter
        );


    document
        .getElementById("categoryFilter")
        .addEventListener(
            "change",
            resetAndFilter
        );


    document
        .getElementById("agencyFilter")
        .addEventListener(
            "change",
            resetAndFilter
        );


    document
        .getElementById("riskFilter")
        .addEventListener(
            "change",
            resetAndFilter
        );


    document
        .getElementById("scoreFilter")
        .addEventListener(
            "input",
            () => {

                document.getElementById(
                    "scoreValue"
                ).textContent =
                    document.getElementById(
                        "scoreFilter"
                    ).value;


                resetAndFilter();

            }
        );


    document
        .getElementById("resetButton")
        .addEventListener(
            "click",
            resetFilters
        );


    document
        .getElementById("exportButton")
        .addEventListener(
            "click",
            exportCurrentResults
        );


    document
        .getElementById("previousPage")
        .addEventListener(
            "click",
            previousPage
        );


    document
        .getElementById("nextPage")
        .addEventListener(
            "click",
            nextPage
        );


    document
        .getElementById("globalSearch")
        .addEventListener(
            "input",
            globalSearch
        );


    document
        .querySelectorAll(
            ".risk-table th[data-sort]"
        )
        .forEach(
            header => {

                header.addEventListener(
                    "click",
                    () =>
                        sortBy(
                            header.dataset.sort
                        )
                );

            }
        );

}


/* =========================================================
   FILTER OPTIONS
========================================================= */

function populateFilters() {

    populateSelect(
        "stateFilter",
        [
            "state",
            "State"
        ]
    );


    populateSelect(
        "districtFilter",
        [
            "district",
            "District"
        ]
    );


    populateSelect(
        "categoryFilter",
        [
            "work_category",
            "category"
        ]
    );


    populateSelect(
        "agencyFilter",
        [
            "implementing_agency",
            "agency"
        ]
    );

}


function populateSelect(
    elementId,
    fields
) {

    const select =
        document.getElementById(
            elementId
        );


    const values =
        uniqueValues(
            allRiskRecords,
            fields
        );


    values.forEach(
        value => {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                value;


            option.textContent =
                value;


            select.appendChild(
                option
            );

        }
    );

}


/* =========================================================
   FILTER
========================================================= */

function resetAndFilter() {

    currentPage = 1;

    applyFilters();

}


function applyFilters() {

    const search =
        document.getElementById(
            "workSearch"
        )
        .value
        .trim()
        .toLowerCase();


    const state =
        document.getElementById(
            "stateFilter"
        ).value;


    const district =
        document.getElementById(
            "districtFilter"
        ).value;


    const category =
        document.getElementById(
            "categoryFilter"
        ).value;


    const agency =
        document.getElementById(
            "agencyFilter"
        ).value;


    const risk =
        document.getElementById(
            "riskFilter"
        ).value;


    const minScore =
        Number(
            document.getElementById(
                "scoreFilter"
            ).value
        );


    filteredRiskRecords =
        allRiskRecords.filter(
            row => {

                /* SEARCH */

                if (search) {

                    const searchable =
                        [

                            getValue(
                                row,
                                [
                                    "record_id",
                                    "work_id",
                                    "id"
                                ]
                            ),

                            getValue(
                                row,
                                [
                                    "work_name",
                                    "description"
                                ]
                            ),

                            getValue(
                                row,
                                [
                                    "state",
                                    "State"
                                ]
                            ),

                            getValue(
                                row,
                                [
                                    "district",
                                    "District"
                                ]
                            ),

                            getValue(
                                row,
                                [
                                    "implementing_agency",
                                    "agency"
                                ]
                            )

                        ]
                        .filter(Boolean)
                        .join(" ")
                        .toLowerCase();


                    if (
                        !searchable.includes(
                            search
                        )
                    ) {

                        return false;

                    }

                }


                /* STATE */

                if (
                    state !== "all" &&
                    String(
                        getValue(
                            row,
                            [
                                "state",
                                "State"
                            ]
                        )
                    ) !== state
                ) {

                    return false;

                }


                /* DISTRICT */

                if (
                    district !== "all" &&
                    String(
                        getValue(
                            row,
                            [
                                "district",
                                "District"
                            ]
                        )
                    ) !== district
                ) {

                    return false;

                }


                /* CATEGORY */

                if (
                    category !== "all" &&
                    String(
                        getValue(
                            row,
                            [
                                "work_category",
                                "category"
                            ]
                        )
                    ) !== category
                ) {

                    return false;

                }


                /* AGENCY */

                if (
                    agency !== "all" &&
                    String(
                        getValue(
                            row,
                            [
                                "implementing_agency",
                                "agency"
                            ]
                        )
                    ) !== agency
                ) {

                    return false;

                }


                /* SCORE */

                const score =
                    getScore(row);


                if (
                    score < minScore
                ) {

                    return false;

                }


                /* RISK */

                if (
                    risk !== "all" &&
                    getRiskTier(row) !== risk
                ) {

                    return false;

                }


                return true;

            }
        );


    sortRecords();

    renderTable();

    setMatchCount(
        filteredRiskRecords.length
    );

}


/* =========================================================
   RISK CLASSIFICATION
========================================================= */

function getScore(row) {

    const score =
        Number(
            row.hybrid_risk_score
        );


    if (
        Number.isFinite(score)
    ) {

        return Math.max(
            0,
            Math.min(
                100,
                score
            )
        );

    }


    return 0;

}


function getRiskTier(row) {

    const score =
        getScore(row);


    if (score >= 80) {

        return "CRITICAL";

    }


    if (score >= 60) {

        return "HIGH";

    }


    if (score >= 30) {

        return "MEDIUM";

    }


    return "LOW";

}


/* =========================================================
   SORTING
========================================================= */

function sortBy(field) {

    if (
        currentSortField === field
    ) {

        currentSortDirection =
            currentSortDirection === "asc"
                ? "desc"
                : "asc";

    } else {

        currentSortField =
            field;

        currentSortDirection =
            "desc";

    }


    sortRecords();

    renderTable();

}


function sortRecords() {

    filteredRiskRecords.sort(
        (a, b) => {

            let first;
            let second;


            if (
                currentSortField ===
                "hybrid_risk_score"
            ) {

                first =
                    getScore(a);

                second =
                    getScore(b);

            } else {

                first =
                    String(
                        getValue(
                            a,
                            [
                                currentSortField
                            ]
                        ) || ""
                    )
                    .toLowerCase();


                second =
                    String(
                        getValue(
                            b,
                            [
                                currentSortField
                            ]
                        ) || ""
                    )
                    .toLowerCase();

            }


            if (
                typeof first === "number"
            ) {

                return currentSortDirection === "asc"
                    ? first - second
                    : second - first;

            }


            return currentSortDirection === "asc"
                ? first.localeCompare(second)
                : second.localeCompare(first);

        }
    );

}


/* =========================================================
   TABLE
========================================================= */

function renderTable() {

    const body =
        document.getElementById(
            "riskTableBody"
        );


    const total =
        filteredRiskRecords.length;


    const totalPages =
        Math.max(
            1,
            Math.ceil(
                total / PAGE_SIZE
            )
        );


    if (
        currentPage > totalPages
    ) {

        currentPage =
            totalPages;

    }


    const start =
        (currentPage - 1) *
        PAGE_SIZE;


    const pageRecords =
        filteredRiskRecords.slice(
            start,
            start + PAGE_SIZE
        );


    if (!pageRecords.length) {

        body.innerHTML = `
            <tr>
                <td colspan="10"
                    class="table-loading">
                    No works match the selected filters.
                </td>
            </tr>
        `;

        updatePagination(
            totalPages
        );

        return;

    }


    body.innerHTML =
        pageRecords
            .map(
                renderRow
            )
            .join("");


    updatePagination(
        totalPages
    );

}


function renderRow(row) {

    const score =
        getScore(row);


    const tier =
        getRiskTier(row);


    const id =
        getValue(
            row,
            [
                "record_id",
                "work_id",
                "id"
            ]
        ) || "—";


    const description =
        getValue(
            row,
            [
                "work_name",
                "description",
                "work_description"
            ]
        ) || "—";


    const state =
        getValue(
            row,
            [
                "state",
                "State"
            ]
        ) || "—";


    const category =
        getValue(
            row,
            [
                "work_category",
                "category"
            ]
        ) || "—";


    const sanctioned =
        getValue(
            row,
            [
                "sanction_amount",
                "sanctioned_amount"
            ]
        );


    const expenditure =
        getValue(
            row,
            [
                "expenditure",
                "expenditure_amount"
            ]
        );


    const signal =
        getPrimarySignal(row);


    const status =
        getValue(
            row,
            [
                "status"
            ]
        ) || "—";


    const width =
        Math.max(
            0,
            Math.min(
                100,
                score
            )
        );


    const idURL =
        encodeURIComponent(
            id
        );


    return `

        <tr>

            <td>

                <span class="
                    risk-tier
                    ${tier.toLowerCase()}
                ">

                    ${tier}

                </span>

            </td>


            <td>

                <strong>
                    ${escapeHTML(id)}
                </strong>

            </td>


            <td
                title="${escapeHTML(description)}">

                ${escapeHTML(
                    truncate(
                        description,
                        42
                    )
                )}

            </td>


            <td>
                ${escapeHTML(state)}
            </td>


            <td>
                ${escapeHTML(category)}
            </td>


            <td class="money">
                ${formatMoney(sanctioned)}
            </td>


            <td class="money">
                ${formatMoney(expenditure)}
            </td>


            <td>

                <div class="score-cell">

                    <strong class="score-number">
                        ${formatScore(score)}
                    </strong>

                    <div class="score-bar">

                        <div
                            class="
                                score-bar-fill
                                ${tier.toLowerCase()}
                            "
                            style="
                                width:${width}%;
                            ">
                        </div>

                    </div>

                </div>

            </td>


            <td>

                <span class="signal-text">
                    ${escapeHTML(signal)}
                </span>

            </td>


            <td>

                <a
                    href="/project/${idURL}"
                    class="open-action">

                    Open →

                </a>

            </td>

        </tr>

    `;

}


/* =========================================================
   PRIMARY SIGNAL
========================================================= */

function getPrimarySignal(row) {

    const reasons =
        getValue(
            row,
            [
                "hybrid_risk_reasons",
                "rule_reasons"
            ]
        );


    if (
        Array.isArray(reasons) &&
        reasons.length
    ) {

        return reasons[0];

    }


    if (reasons) {

        return String(
            reasons
        )
        .split(",")[0]
        .trim();

    }


    const overrun =
        Number(
            getValue(
                row,
                [
                    "cost_overrun_amount"
                ]
            )
        );


    if (
        Number.isFinite(overrun) &&
        overrun > 0
    ) {

        return "Cost anomaly";

    }


    const gap =
        Number(
            getValue(
                row,
                [
                    "progress_expenditure_gap"
                ]
            )
        );


    if (
        Number.isFinite(gap) &&
        gap > 25
    ) {

        return "Progress mismatch";

    }


    const delay =
        Number(
            getValue(
                row,
                [
                    "delay_days"
                ]
            )
        );


    if (
        Number.isFinite(delay) &&
        delay > 30
    ) {

        return "Timeline delay";

    }


    if (
        row.ml_anomaly === true ||
        row.ml_anomaly === 1 ||
        row.ml_anomaly === "1"
    ) {

        return "ML anomaly";

    }


    return "Risk signal";

}


/* =========================================================
   PAGINATION
========================================================= */

function updatePagination(
    totalPages
) {

    document.getElementById(
        "pageInfo"
    ).textContent =
        `Page ${currentPage} of ${totalPages}`;


    document.getElementById(
        "previousPage"
    ).disabled =
        currentPage <= 1;


    document.getElementById(
        "nextPage"
    ).disabled =
        currentPage >= totalPages;

}


function previousPage() {

    if (
        currentPage > 1
    ) {

        currentPage--;

        renderTable();

    }

}


function nextPage() {

    const totalPages =
        Math.max(
            1,
            Math.ceil(
                filteredRiskRecords.length /
                PAGE_SIZE
            )
        );


    if (
        currentPage < totalPages
    ) {

        currentPage++;

        renderTable();

    }

}


/* =========================================================
   RESET
========================================================= */

function resetFilters() {

    document.getElementById(
        "workSearch"
    ).value = "";


    document.getElementById(
        "stateFilter"
    ).value = "all";


    document.getElementById(
        "districtFilter"
    ).value = "all";


    document.getElementById(
        "categoryFilter"
    ).value = "all";


    document.getElementById(
        "agencyFilter"
    ).value = "all";


    document.getElementById(
        "riskFilter"
    ).value = "all";


    document.getElementById(
        "scoreFilter"
    ).value = 0;


    document.getElementById(
        "scoreValue"
    ).textContent = "0";


    currentPage = 1;


    applyFilters();

}


/* =========================================================
   GLOBAL SEARCH
========================================================= */

function globalSearch() {

    const value =
        document.getElementById(
            "globalSearch"
        ).value;


    document.getElementById(
        "workSearch"
    ).value = value;


    resetAndFilter();

}


/* =========================================================
   EXPORT
========================================================= */

function exportCurrentResults() {

    if (
        !filteredRiskRecords.length
    ) {

        alert(
            "There are no records to export."
        );

        return;

    }


    const columns = [

        "record_id",
        "state",
        "district",
        "work_category",
        "implementing_agency",
        "sanction_amount",
        "expenditure",
        "hybrid_risk_score",
        "hybrid_risk_level",
        "inspection_priority",
        "status"

    ];


    const rows =
        filteredRiskRecords.map(
            row =>
                columns.map(
                    column =>
                        csvValue(
                            row[column]
                        )
                )
        );


    const csv =
        [
            columns.join(","),
            ...rows.map(
                row =>
                    row.join(",")
            )
        ]
        .join("\n");


    const blob =
        new Blob(
            [csv],
            {
                type:
                    "text/csv;charset=utf-8;"
            }
        );


    const url =
        URL.createObjectURL(
            blob
        );


    const link =
        document.createElement(
            "a"
        );


    link.href = url;

    link.download =
        "mplads_sentinel_risk_monitor.csv";


    document.body.appendChild(
        link
    );


    link.click();


    link.remove();


    URL.revokeObjectURL(
        url
    );

}


/* =========================================================
   HELPERS
========================================================= */

function getValue(
    row,
    fields
) {

    for (
        const field of fields
    ) {

        if (
            row[field] !== undefined &&
            row[field] !== null &&
            row[field] !== ""
        ) {

            return row[field];

        }

    }


    return null;

}


function uniqueValues(
    records,
    fields
) {

    const values = [];


    records.forEach(
        row => {

            const value =
                getValue(
                    row,
                    fields
                );


            if (
                value !== null &&
                value !== undefined &&
                String(value).trim()
            ) {

                values.push(
                    String(value)
                );

            }

        }
    );


    return [
        ...new Set(values)
    ].sort();

}


function formatMoney(
    value
) {

    if (
        value === null ||
        value === undefined ||
        value === ""
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


function formatScore(
    value
) {

    if (
        !Number.isFinite(value)
    ) {

        return "—";

    }


    return Math.round(
        value
    );

}


function formatNumber(
    value
) {

    return Number(
        value || 0
    ).toLocaleString(
        "en-IN"
    );

}


function truncate(
    value,
    length
) {

    const text =
        String(value);


    if (
        text.length <= length
    ) {

        return text;

    }


    return text.slice(
        0,
        length
    ) + "...";

}


function escapeHTML(
    value
) {

    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );

}


function csvValue(
    value
) {

    if (
        value === undefined ||
        value === null
    ) {

        return "";

    }


    const text =
        Array.isArray(value)
            ? value.join("; ")
            : String(value);


    return `"${text.replaceAll(
        '"',
        '""'
    )}"`;

}


function setMatchCount(
    count
) {

    document.getElementById(
        "matchCount"
    ).textContent =
        `${formatNumber(count)} works match filters`;

}


function updateSidebarTime() {

    const element =
        document.getElementById(
            "sidebarUpdated"
        );


    if (!element) return;


    element.textContent =
        new Date().toLocaleString(
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