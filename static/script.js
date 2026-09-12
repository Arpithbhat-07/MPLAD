/* =====================================================
   MPLAD AI MONITORING - FRONTEND
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* ---------------------------------------------
       SEARCH PROJECTS
    --------------------------------------------- */

    const searchInput =
        document.getElementById("searchInput");

    const riskFilter =
        document.getElementById("riskFilter");

    const projectRows =
        document.querySelectorAll(".project-item");


    function filterProjects() {

        if (!searchInput) return;

        const search =
            searchInput.value.toLowerCase().trim();

        const risk =
            riskFilter
                ? riskFilter.value.toLowerCase()
                : "all";


        projectRows.forEach(function (row) {

            const text =
                row.dataset.search || "";

            const rowRisk =
                row.dataset.risk || "";

            const searchMatch =
                text.includes(search);

            const riskMatch =
                risk === "all" ||
                rowRisk === risk;


            if (searchMatch && riskMatch) {

                row.style.display = "grid";

            } else {

                row.style.display = "none";

            }

        });

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterProjects
        );

    }


    if (riskFilter) {

        riskFilter.addEventListener(
            "change",
            filterProjects
        );

    }


    /* ---------------------------------------------
       SMOOTH SCROLL
    --------------------------------------------- */

    document.querySelectorAll(
        'a[href^="#"]'
    ).forEach(function (link) {

        link.addEventListener(
            "click",
            function (event) {

                const targetId =
                    this.getAttribute("href");

                if (
                    targetId &&
                    targetId !== "#"
                ) {

                    const target =
                        document.querySelector(targetId);

                    if (target) {

                        event.preventDefault();

                        target.scrollIntoView({
                            behavior: "smooth",
                            block: "start"
                        });

                    }

                }

            }
        );

    });


    /* ---------------------------------------------
       BUTTON HOVER EFFECT
    --------------------------------------------- */

    document.querySelectorAll(
        "button"
    ).forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                this.style.transform =
                    "scale(0.98)";

                setTimeout(() => {

                    this.style.transform =
                        "scale(1)";

                }, 100);

            }
        );

    });


    /* ---------------------------------------------
       AUTO UPDATE SYSTEM STATUS
    --------------------------------------------- */

    const statusDot =
        document.querySelector(".status-dot");

    if (statusDot) {

        setInterval(function () {

            statusDot.style.opacity =
                statusDot.style.opacity === "0.5"
                    ? "1"
                    : "0.5";

        }, 1200);

    }


    /* ---------------------------------------------
       PROGRESS ANIMATION
    --------------------------------------------- */

    const progressBars =
        document.querySelectorAll(
            ".progress-large div, .mini-progress div"
        );


    progressBars.forEach(function (bar) {

        const originalWidth =
            bar.style.width;

        bar.style.width = "0";

        setTimeout(function () {

            bar.style.width =
                originalWidth;

        }, 200);

    });

});


/* =====================================================
   REVIEW PROJECTS BUTTON
===================================================== */

function scrollToProjects() {

    const section =
        document.getElementById("projects");

    if (section) {

        section.scrollIntoView({
            behavior: "smooth"
        });

    }

}


/* =====================================================
   SIMPLE ALERT
===================================================== */

function showNotification(message) {

    const notification =
        document.createElement("div");

    notification.innerText =
        message;

    notification.style.position =
        "fixed";

    notification.style.bottom =
        "25px";

    notification.style.right =
        "25px";

    notification.style.background =
        "#0b2a4a";

    notification.style.color =
        "white";

    notification.style.padding =
        "12px 18px";

    notification.style.borderRadius =
        "7px";

    notification.style.fontSize =
        "12px";

    notification.style.zIndex =
        "9999";

    document.body.appendChild(
        notification
    );


    setTimeout(function () {

        notification.remove();

    }, 2500);

}