document.addEventListener("DOMContentLoaded", function () {
    const button = document.getElementById("levelButton");
    const input = document.getElementById("levelInput");

    document.querySelectorAll(".dropdown-item").forEach(item => {
        item.addEventListener("click", function (e) {
            e.preventDefault();

            const level = this.dataset.level;

            button.textContent = level;
            input.value = level;
        });
    });
});