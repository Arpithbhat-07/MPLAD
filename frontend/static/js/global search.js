/* =========================================================
   MPLADS SENTINEL — GLOBAL SEARCH
   Works across all frontend pages
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const searchInput = document.getElementById("globalSearch");

    if (!searchInput) {
        return;
    }

    let resultsBox = null;
    let records = [];

    /* ---------------------------------------------------------
       CREATE SEARCH RESULTS CONTAINER
       --------------------------------------------------------- */

    function createResultsBox() {

        resultsBox = document.createElement("div");

        resultsBox.id = "globalSearchResults";

        resultsBox.style.position = "absolute";
        resultsBox.style.top = "calc(100% + 4px)";
        resultsBox.style.left = "0";
        resultsBox.style.right = "0";
        resultsBox.style.zIndex = "9999";

        resultsBox.style.background = "#0d1014";
        resultsBox.style.border = "1px solid #252b35";
        resultsBox.style.borderRadius = "6px";

        resultsBox.style.maxHeight = "420px";
        resultsBox.style.overflowY = "auto";

        resultsBox.style.display = "none";

        searchInput.parentElement.style.position = "relative";

        searchInput.parentElement.appendChild(resultsBox);
    }


    /* ---------------------------------------------------------
       LOAD PROJECT DATA
       --------------------------------------------------------- */

    async function loadRecords() {

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

            records =
                Array.isArray(result.data)
                    ? result.data
                    : [];

            console.log(
                "Global search records:",
                records.length
            );

        } catch (error) {

            console.error(
                "Global search failed:",
                error
            );

            records = [];
        }
    }


    /* ---------------------------------------------------------
       GET VALUE FROM MULTIPLE POSSIBLE FIELD NAMES
       --------------------------------------------------------- */

    function getValue(row, keys) {

        for (const key of keys) {

            if (
                row[key] !== undefined &&
                row[key] !== null &&
                String(row[key]).trim() !== ""
            ) {
                return row[key];
            }

        }

        return null;
    }


    /* ---------------------------------------------------------
       ESCAPE HTML
       --------------------------------------------------------- */

    function escapeHTML(value) {

        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }


    /* ---------------------------------------------------------
       SHOW RESULTS
       --------------------------------------------------------- */

    function showResults(query) {

        if (!resultsBox) {
            return;
        }

        query = query.trim().toLowerCase();

        if (!query) {

            resultsBox.innerHTML = "";
            resultsBox.style.display = "none";

            return;
        }


        const matches = records
            .filter(row => {

                const searchableText = [

                    getValue(row, [
                        "record_id",
                        "work_id",
                        "id"
                    ]),

                    getValue(row, [
                        "district",
                        "District"
                    ]),

                    getValue(row, [
                        "state",
                        "State"
                    ]),

                    getValue(row, [
                        "implementing_agency",
                        "agency",
                        "Agency"
                    ]),

                    getValue(row, [
                        "work_category",
                        "category"
                    ]),

                    getValue(row, [
                        "work_name",
                        "work_description",
                        "description"
                    ])

                ]
                .filter(Boolean)
                .join(" ")
                .toLowerCase();

                return searchableText.includes(query);
            })
            .slice(0, 8);


        if (!matches.length) {

            resultsBox.innerHTML = `
                <div style="
                    padding: 18px;
                    color: #7d8796;
                    font-size: 13px;
                ">
                    No matching works found.
                </div>
            `;

            resultsBox.style.display = "block";

            return;
        }


        resultsBox.innerHTML = matches
            .map(row => {

                const id = getValue(row, [
                    "record_id",
                    "work_id",
                    "id"
                ]) || "—";


                const district = getValue(row, [
                    "district",
                    "District"
                ]) || "Unknown district";


                const state = getValue(row, [
                    "state",
                    "State"
                ]) || "";


                const category = getValue(row, [
                    "work_category",
                    "category"
                ]) || "Unknown category";


                const score = Number(
                    getValue(row, [
                        "hybrid_risk_score",
                        "risk_score"
                    ])
                );


                const risk =
                    getValue(row, [
                        "hybrid_risk_level",
                        "risk_level",
                        "risk"
                    ]) || "LOW";


                return `
                    <a
                        href="/project/${encodeURIComponent(id)}"
                        class="global-search-result"
                        style="
                            display:block;
                            text-decoration:none;
                            padding:12px 14px;
                            border-bottom:1px solid #20252d;
                            color:#ffffff;
                            transition:background 0.15s ease;
                        "
                    >

                        <div style="
                            display:flex;
                            align-items:center;
                            gap:10px;
                        ">

                            ${
                                Number.isFinite(score)
                                    ? `
                                        <span style="
                                            color:#ff5b61;
                                            font-weight:700;
                                            min-width:24px;
                                        ">
                                            ${Math.round(score)}
                                        </span>
                                      `
                                    : ""
                            }

                            <div>

                                <div style="
                                    font-size:13px;
                                    font-weight:700;
                                ">
                                    ${escapeHTML(id)}
                                </div>

                                <div style="
                                    margin-top:3px;
                                    color:#7d8796;
                                    font-size:11px;
                                ">
                                    ${escapeHTML(category)}
                                    ·
                                    ${escapeHTML(district)}
                                    ${
                                        state
                                            ? ", " +
                                              escapeHTML(state)
                                            : ""
                                    }
                                </div>

                            </div>

                        </div>

                    </a>
                `;
            })
            .join("");


        resultsBox.style.display = "block";
    }


    /* ---------------------------------------------------------
       INITIALIZE
       --------------------------------------------------------- */

    createResultsBox();

    loadRecords();


    /* ---------------------------------------------------------
       LIVE SEARCH
       --------------------------------------------------------- */

    searchInput.addEventListener(
        "input",
        () => {

            showResults(
                searchInput.value
            );

        }
    );


    /* ---------------------------------------------------------
       CLOSE WHEN CLICKING OUTSIDE
       --------------------------------------------------------- */

    document.addEventListener(
        "click",
        event => {

            if (
                !searchInput.parentElement.contains(
                    event.target
                )
            ) {

                if (resultsBox) {
                    resultsBox.style.display = "none";
                }

            }

        }
    );


    /* ---------------------------------------------------------
       "/" SHORTCUT
       --------------------------------------------------------- */

    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "/" &&
                document.activeElement !== searchInput &&
                !["INPUT", "TEXTAREA"].includes(
                    document.activeElement.tagName
                )
            ) {

                event.preventDefault();

                searchInput.focus();
            }

            if (
                event.key === "Escape"
            ) {

                searchInput.value = "";

                if (resultsBox) {
                    resultsBox.style.display = "none";
                }

            }

        }
    );

});