document.addEventListener("DOMContentLoaded", function () {
    const filterForm = document.getElementById('filterForm');
    const searchInput = document.getElementById('searchInput');
    let typingTimer;
    const doneTypingInterval = 500; 

    searchInput.addEventListener('input', function () {

        typingTimer = setTimeout(function () {
            filterForm.submit();
        }, doneTypingInterval);
    });

    if (searchInput.value) {
        searchInput.focus();
        let val = searchInput.value;
        searchInput.value = '';
        searchInput.value = val;
    }

    const selects = document.querySelectorAll('.auto-submit');
    selects.forEach(function (select) {
        select.addEventListener('change', function () {
            filterForm.submit();
        });
    });
});