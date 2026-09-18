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

    /* ---------- Xóa khóa học khỏi danh sách gợi ý ---------- */
    var bulkBar = document.getElementById('rec-bulk-actions');
    if (bulkBar) {
        var checkboxes = document.querySelectorAll('.rec-select-checkbox');
        var selectedCountEl = document.getElementById('rec-selected-count');

        function updateBulkBar() {
            var checked = document.querySelectorAll('.rec-select-checkbox:checked');
            bulkBar.style.display = checked.length > 0 ? 'flex' : 'none';
            selectedCountEl.textContent = checked.length + ' khóa học được chọn';
        }

        checkboxes.forEach(function (cb) {
            cb.addEventListener('change', updateBulkBar);
        });

        window.dismissSelectedCourses = function () {
            var checked = Array.from(document.querySelectorAll('.rec-select-checkbox:checked'))
                .map(function (cb) { return parseInt(cb.value, 10); });
            if (!checked.length) return;
            dismissCourses(checked);
        };

        // Nút "x" xóa nhanh từng card
        document.querySelectorAll('.btn-dismiss-course').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var courseId = parseInt(btn.getAttribute('data-course-id'), 10);
                dismissCourses([courseId]);
            });
        });

        function dismissCourses(courseIds) {
            if (!confirm(courseIds.length > 1
                ? 'Xóa ' + courseIds.length + ' khóa học khỏi danh sách gợi ý?'
                : 'Xóa khóa học này khỏi danh sách gợi ý?')) return;

            fetch('/courses/recommended/dismiss', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ course_ids: courseIds })
            })
            .then(function (res) { return res.json().then(function (data) {
                if (!res.ok) throw new Error(data.error || 'Có lỗi xảy ra');
                return data;
            }); })
            .then(function () {
                courseIds.forEach(function (id) {
                    var checkboxEl = document.querySelector('.rec-select-checkbox[value="' + id + '"]');
                    var cardEl = checkboxEl ? checkboxEl.closest('.course-rec-card') : null;
                    if (cardEl) {
                        cardEl.classList.add('is-removing');
                        setTimeout(function () { cardEl.closest('.col-md-6').remove(); }, 250);
                    }
                });
                updateBulkBar();
            })
            .catch(function (err) {
                alert('Không xóa được: ' + err.message);
            });
        }
    }
});