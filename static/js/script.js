function filterCourses(level, button) {

    const cards =
        document.querySelectorAll(".course-card");

    const buttons =
        document.querySelectorAll(".filter-btn");

    buttons.forEach(btn => {
        btn.classList.remove("active");
    });

    button.classList.add("active");

    let visible = 0;

    cards.forEach(card => {

        const cardLevel =
            card.dataset.level;

        if (
            level === "all" ||
            cardLevel === level
        ) {

            card.style.display = "block";

            visible++;

        } else {

            card.style.display = "none";

        }

    });

    document.getElementById("noCourses").style.display =
        visible === 0 ? "block" : "none";
}


function searchCourses() {

    const search =
        document
            .getElementById("courseSearch")
            .value
            .toLowerCase()
            .trim();

    const cards =
        document.querySelectorAll(".course-card");

    let visible = 0;

    cards.forEach(card => {

        const title =
            card.dataset.title;

        if (title.includes(search)) {

            card.style.display = "block";

            visible++;

        } else {

            card.style.display = "none";

        }

    });

    document.getElementById("noCourses").style.display =
        visible === 0 ? "block" : "none";
}
