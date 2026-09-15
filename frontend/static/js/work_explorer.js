"use strict";


/* =========================================================
   WORK EXPLORER
========================================================= */

const cards =
    Array.from(
        document.querySelectorAll(
            ".project-card"
        )
    );


const tabs =
    Array.from(
        document.querySelectorAll(
            ".category-tab"
        )
    );


const searchInput =
    document.getElementById(
        "workSearch"
    );


const globalSearch =
    document.getElementById(
        "globalSearch"
    );


let activeCategory = "all";


/* =========================================================
   FILTER
========================================================= */

function filterCards() {

    const search =
        (
            searchInput?.value ||
            globalSearch?.value ||
            ""
        )
        .trim()
        .toLowerCase();


    cards.forEach(
        card => {

            const category =
                (
                    card.dataset.category ||
                    ""
                )
                .trim()
                .toLowerCase();


            const searchable =
                (
                    card.dataset.search ||
                    ""
                )
                .toLowerCase();


            const categoryMatch =
                activeCategory === "all" ||
                category ===
                    activeCategory.toLowerCase();


            const searchMatch =
                !search ||
                searchable.includes(
                    search
                );


            card.style.display =
                categoryMatch &&
                searchMatch
                    ? ""
                    : "none";

        }
    );

}


/* =========================================================
   CATEGORY TABS
========================================================= */

tabs.forEach(
    tab => {

        tab.addEventListener(
            "click",
            () => {

                tabs.forEach(
                    item => {

                        item.classList.remove(
                            "active"
                        );

                    }
                );


                tab.classList.add(
                    "active"
                );


                activeCategory =
                    tab.dataset.category ||
                    "all";


                filterCards();

            }
        );

    }
);


/* =========================================================
   SEARCH
========================================================= */

if (searchInput) {

    searchInput.addEventListener(
        "input",
        filterCards
    );

}


if (globalSearch) {

    globalSearch.addEventListener(
        "input",
        () => {

            if (searchInput) {

                searchInput.value =
                    globalSearch.value;

            }

            filterCards();

        }
    );

}


/* =========================================================
   KEYBOARD SEARCH
========================================================= */

document.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "/" &&
            document.activeElement.tagName !==
                "INPUT"
        ) {

            event.preventDefault();

            searchInput?.focus();

        }

    }
);


/* =========================================================
   INITIAL
========================================================= */

filterCards();