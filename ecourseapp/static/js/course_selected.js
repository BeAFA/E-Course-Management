document.addEventListener('DOMContentLoaded', function () {
    const checkAll = document.getElementById('check-all');
    const rowChecks = document.querySelectorAll('.row-check');
    const bulkActions = document.getElementById('bulk-actions');
    const selectedCount = document.getElementById('selected-count');

    function getSelectedIds() {
        return Array.from(document.querySelectorAll('.row-check:checked'))
                     .map(cb => cb.value);
    }

    function toggleBulkBar() {
        const ids = getSelectedIds();
        bulkActions.style.display = ids.length > 0 ? 'flex' : 'none';
        selectedCount.textContent = `${ids.length} khóa học được chọn`;
    }

    // Đồng bộ trạng thái checkbox "chọn tất cả" dựa trên các dòng hiện tại
    function syncCheckAllState() {
        if (!checkAll) return;
        const total = rowChecks.length;
        const checkedCount = getSelectedIds().length;

        if (checkedCount === 0) {
            checkAll.checked = false;
            checkAll.indeterminate = false;
        } else if (checkedCount === total) {
            checkAll.checked = true;
            checkAll.indeterminate = false;
        } else {
            // Một số được chọn, một số chưa -> hiện trạng thái "lưng chừng"
            checkAll.checked = false;
            checkAll.indeterminate = true;
        }
    }

    if (checkAll) {
        checkAll.addEventListener('change', function () {
            rowChecks.forEach(cb => cb.checked = checkAll.checked);
            checkAll.indeterminate = false;
            toggleBulkBar();
        });
    }

    rowChecks.forEach(cb => cb.addEventListener('change', function () {
        syncCheckAllState();
        toggleBulkBar();
    }));

    window.updateActiveStatus = function (isActive) {
        const ids = getSelectedIds();
        if (ids.length === 0) return;

        fetch("/courses/bulk-update-status", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                course_ids: ids,
                is_active: isActive
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.message || 'Có lỗi xảy ra, vui lòng thử lại.');
            }
        })
        .catch(err => {
            console.error(err);
            alert('Không thể kết nối tới server.');
        });
    };
});