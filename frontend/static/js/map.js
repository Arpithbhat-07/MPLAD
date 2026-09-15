function initializeMap(records) {

    const container =
        document.getElementById(
            "indiaMap"
        );


    if (!container) return;


    /*
     * We intentionally do not draw
     * fake geographical values.
     *
     * The state ranking beside the map
     * is calculated directly from the
     * dataset.
     */

    const states =
        buildStateRiskData(
            records
        );


    if (!states.length) {

        container.innerHTML = `
            <div class="map-placeholder">

                <div class="map-symbol">
                    ◉
                </div>

                <strong>
                    Geographic data unavailable
                </strong>

                <span>
                    No usable state information
                    exists in the current dataset.
                </span>

            </div>
        `;

        return;

    }


    /*
     * Show a clean geographic-intelligence
     * visualization without inventing
     * state boundaries or risk values.
     */

    const totalHigh =
        states.reduce(
            (
                total,
                state
            ) =>
                total + state.high,
            0
        );


    const totalWorks =
        states.reduce(
            (
                total,
                state
            ) =>
                total + state.works,
            0
        );


    container.innerHTML = `

        <div class="map-placeholder">

            <div
                class="map-symbol"
                style="
                    width:110px;
                    height:110px;
                    font-size:40px;
                    border-color:#30405b;
                    background:
                        radial-gradient(
                            circle,
                            #152033,
                            #0d1117
                        );
                ">
                🇮🇳
            </div>

            <strong>
                India — Risk Intelligence
            </strong>

            <span>
                ${formatMapNumber(states.length)}
                states represented ·
                ${formatMapNumber(totalWorks)}
                works analyzed ·
                ${formatMapNumber(totalHigh)}
                high-risk works
            </span>

        </div>
    `;

}


function buildStateRiskData(
    records
) {

    const result = {};


    records.forEach(row => {

        const state =
            row.state ||
            row.State;


        if (!state) return;


        if (!result[state]) {

            result[state] = {

                works: 0,

                high: 0,

                medium: 0,

                low: 0

            };

        }


        result[state].works++;


        const risk =
            String(
                row.hybrid_risk_level || ""
            ).toUpperCase();


        if (risk === "HIGH") {

            result[state].high++;

        } else if (
            risk === "MEDIUM"
        ) {

            result[state].medium++;

        } else {

            result[state].low++;

        }

    });


    return Object.entries(result)
        .map(
            ([state, data]) => ({
                state,
                ...data
            })
        )
        .sort(
            (a, b) =>
                b.high - a.high
        );

}


function formatMapNumber(
    value
) {

    return Number(value || 0)
        .toLocaleString(
            "en-IN"
        );

}