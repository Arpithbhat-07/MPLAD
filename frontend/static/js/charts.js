let riskChartInstance = null;
let trendChartInstance = null;
let fundChartInstance = null;


/* =====================================================
   CHART INITIALIZATION
===================================================== */

function initializeCharts(records) {

    createRiskChart(records);

    createTrendChart(records);

    createFundChart(records);

}


/* =====================================================
   RISK DONUT
===================================================== */

function createRiskChart(records) {

    const canvas =
        document.getElementById(
            "riskChart"
        );


    if (!canvas) return;


    if (riskChartInstance) {

        riskChartInstance.destroy();

    }


    const high =
        records.filter(
            row =>
                String(
                    row.hybrid_risk_level || ""
                ).toUpperCase() === "HIGH"
        ).length;


    const medium =
        records.filter(
            row =>
                String(
                    row.hybrid_risk_level || ""
                ).toUpperCase() === "MEDIUM"
        ).length;


    const low =
        records.filter(
            row =>
                String(
                    row.hybrid_risk_level || ""
                ).toUpperCase() === "LOW"
        ).length;


    riskChartInstance =
        new Chart(
            canvas,
            {

                type: "doughnut",

                data: {

                    labels: [
                        "High",
                        "Medium",
                        "Low"
                    ],

                    datasets: [{

                        data: [
                            high,
                            medium,
                            low
                        ],

                        backgroundColor: [
                            "#ff4e58",
                            "#ff982f",
                            "#4fc77b"
                        ],

                        borderWidth: 0,

                        spacing: 2

                    }]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    cutout: "73%",

                    plugins: {

                        legend: {
                            display: false
                        },

                        tooltip: {

                            backgroundColor:
                                "#171b21",

                            borderColor:
                                "#303640",

                            borderWidth: 1,

                            titleColor:
                                "#ffffff",

                            bodyColor:
                                "#b7c0cc"

                        }

                    }

                }

            }
        );

}


/* =====================================================
   TREND
===================================================== */

function createTrendChart(records) {

    const canvas =
        document.getElementById(
            "trendChart"
        );


    const unavailable =
        document.getElementById(
            "trendUnavailable"
        );


    if (!canvas) return;


    if (trendChartInstance) {

        trendChartInstance.destroy();

        trendChartInstance = null;

    }


    /*
     * IMPORTANT:
     * We do NOT create artificial months.
     *
     * If the dataset doesn't contain
     * usable dates, the chart remains
     * unavailable.
     */

    const dateField =
        findUsableDateField(records);


    if (!dateField) {

        canvas.style.display = "none";

        if (unavailable) {

            unavailable.style.display =
                "flex";

        }

        return;

    }


    const grouped = {};


    records.forEach(row => {

        const raw =
            row[dateField];


        const date =
            new Date(raw);


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return;

        }


        const key =
            date.toISOString()
                .slice(0, 7);


        if (!grouped[key]) {

            grouped[key] = {
                high: 0,
                medium: 0,
                low: 0
            };

        }


        const risk =
            String(
                row.hybrid_risk_level || ""
            ).toUpperCase();


        if (risk === "HIGH") {

            grouped[key].high++;

        } else if (risk === "MEDIUM") {

            grouped[key].medium++;

        } else {

            grouped[key].low++;

        }

    });


    const months =
        Object.keys(grouped)
            .sort()
            .slice(-12);


    if (!months.length) {

        canvas.style.display = "none";

        if (unavailable) {

            unavailable.style.display =
                "flex";

        }

        return;

    }


    canvas.style.display = "block";

    if (unavailable) {

        unavailable.style.display =
            "none";

    }


    trendChartInstance =
        new Chart(
            canvas,
            {

                type: "line",

                data: {

                    labels:
                        months.map(
                            formatMonth
                        ),

                    datasets: [

                        {
                            label: "High",

                            data:
                                months.map(
                                    month =>
                                        grouped[
                                            month
                                        ].high
                                ),

                            borderColor:
                                "#ff4e58",

                            backgroundColor:
                                "transparent",

                            tension: .35,

                            pointRadius: 2,

                            borderWidth: 2

                        },

                        {
                            label: "Medium",

                            data:
                                months.map(
                                    month =>
                                        grouped[
                                            month
                                        ].medium
                                ),

                            borderColor:
                                "#ff982f",

                            backgroundColor:
                                "transparent",

                            tension: .35,

                            pointRadius: 2,

                            borderWidth: 2

                        },

                        {
                            label: "Low",

                            data:
                                months.map(
                                    month =>
                                        grouped[
                                            month
                                        ].low
                                ),

                            borderColor:
                                "#4fc77b",

                            backgroundColor:
                                "transparent",

                            tension: .35,

                            pointRadius: 2,

                            borderWidth: 2

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    interaction: {
                        mode: "index",
                        intersect: false
                    },

                    plugins: {

                        legend: {

                            labels: {

                                color: "#8c96a5",

                                font: {
                                    size: 9
                                }
                            }

                        }

                    },

                    scales: {

                        x: {

                            grid: {
                                color:
                                    "#1c2229"
                            },

                            ticks: {

                                color:
                                    "#687384",

                                font: {
                                    size: 8
                                }

                            }

                        },

                        y: {

                            beginAtZero: true,

                            grid: {
                                color:
                                    "#1c2229"
                            },

                            ticks: {

                                color:
                                    "#687384",

                                font: {
                                    size: 8
                                }

                            }

                        }

                    }

                }

            }
        );

}


/* =====================================================
   SANCTIONED VS EXPENDITURE
===================================================== */

function createFundChart(records) {

    const canvas =
        document.getElementById(
            "fundChart"
        );


    const unavailable =
        document.getElementById(
            "fundUnavailable"
        );


    if (!canvas) return;


    if (fundChartInstance) {

        fundChartInstance.destroy();

        fundChartInstance = null;

    }


    const sanctionedField =
        findField(
            records,
            [
                "sanction_amount",
                "sanctioned_amount"
            ]
        );


    const expenditureField =
        findField(
            records,
            [
                "expenditure",
                "expenditure_amount"
            ]
        );


    if (
        !sanctionedField ||
        !expenditureField
    ) {

        canvas.style.display =
            "none";


        if (unavailable) {

            unavailable.style.display =
                "flex";

        }

        return;

    }


    const sanctioned =
        sumNumeric(
            records,
            sanctionedField
        );


    const expenditure =
        sumNumeric(
            records,
            expenditureField
        );


    if (
        sanctioned === null ||
        expenditure === null
    ) {

        canvas.style.display =
            "none";


        if (unavailable) {

            unavailable.style.display =
                "flex";

        }

        return;

    }


    canvas.style.display =
        "block";


    if (unavailable) {

        unavailable.style.display =
            "none";

    }


    fundChartInstance =
        new Chart(
            canvas,
            {

                type: "bar",

                data: {

                    labels: [
                        "Available Records"
                    ],

                    datasets: [

                        {
                            label: "Sanctioned",

                            data: [
                                sanctioned
                            ],

                            backgroundColor:
                                "#34415b",

                            borderRadius: 4

                        },

                        {
                            label: "Expenditure",

                            data: [
                                expenditure
                            ],

                            backgroundColor:
                                "#4d91ff",

                            borderRadius: 4

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            labels: {

                                color:
                                    "#8993a2",

                                font: {
                                    size: 9
                                }

                            }

                        }

                    },

                    scales: {

                        x: {

                            grid: {
                                display: false
                            },

                            ticks: {
                                color:
                                    "#687384"
                            }

                        },

                        y: {

                            beginAtZero: true,

                            grid: {

                                color:
                                    "#1c2229"

                            },

                            ticks: {

                                color:
                                    "#687384",

                                font: {
                                    size: 8
                                }

                            }

                        }

                    }

                }

            }
        );

}


/* =====================================================
   HELPERS
===================================================== */

function findUsableDateField(
    records
) {

    const fields = [

        "actual_completion_date",
        "start_date",
        "expected_completion_date",
        "sanction_date"

    ];


    for (
        const field of fields
    ) {

        const usable =
            records.some(
                row => {

                    if (!row[field])
                        return false;


                    const date =
                        new Date(
                            row[field]
                        );


                    return !Number.isNaN(
                        date.getTime()
                    );

                }
            );


        if (usable) {

            return field;

        }

    }


    return null;

}


function findField(
    records,
    fields
) {

    for (
        const field of fields
    ) {

        if (
            records.some(
                row =>
                    row[field] !== undefined &&
                    row[field] !== null &&
                    row[field] !== ""
            )
        ) {

            return field;

        }

    }


    return null;

}


function sumNumeric(
    records,
    field
) {

    let total = 0;

    let found = false;


    records.forEach(row => {

        const value =
            Number(
                row[field]
            );


        if (
            Number.isFinite(value)
        ) {

            total += value;

            found = true;

        }

    });


    return found
        ? total
        : null;

}


function formatMonth(
    value
) {

    const date =
        new Date(
            value + "-01"
        );


    return date.toLocaleDateString(
        "en-IN",
        {
            month: "short"
        }
    );

}