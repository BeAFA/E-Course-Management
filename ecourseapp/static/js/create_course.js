document.addEventListener('DOMContentLoaded', () => {
    var addBtn = document.getElementById('btnAddTag');
    var input = document.getElementById('newTagInput');
    var msgEl = document.getElementById('tagCreateMsg');
    var container = document.getElementById('tagListContainer');

    document.querySelector('form').addEventListener('submit', function (e) {
        const checkedTags = document.querySelectorAll('input[name="tag_ids"]:checked');
        if (checkedTags.length === 0) {
            e.preventDefault();
            alert('Vui lòng chọn ít nhất 1 thẻ Tag cho khóa học trước khi lưu!');
        }
    });

    if (!addBtn) return; // trang không có khung tag (phòng hờ tái dùng file JS)

    function showMessage(text, type) {
        msgEl.textContent = text;
        msgEl.className = 'small mb-2 text-' + type;
    }

    function addTagCheckbox(tag, checked) {
        var checkboxId = 'tag_' + tag.id;
        var existingCb = document.getElementById(checkboxId);
        if (existingCb) {
            existingCb.checked = true;
            return;
        }

        var placeholder = document.getElementById('noTagPlaceholder');
        if (placeholder) placeholder.remove();

        var wrap = document.createElement('div');
        wrap.className = 'form-check-inline m-0';
        wrap.innerHTML =
            '<input class="btn-check" type="checkbox" name="tag_ids" id="' + checkboxId +
            '" value="' + tag.id + '" autocomplete="off"' + (checked ? ' checked' : '') + '>' +
            '<label class="btn btn-outline-primary btn-sm rounded-pill px-3 py-1" for="' + checkboxId +
            '"># ' + tag.name + '</label>';
        container.appendChild(wrap);
    }

    function handleAddTag() {
        var name = input.value.trim();
        showMessage('', '');

        if (!name) {
            showMessage('Vui lòng nhập tên tag.', 'danger');
            return;
        }

        // Nếu tag đã hiển thị sẵn trong danh sách (trùng tên, không phân biệt hoa/thường)
        // -> chỉ cần tick chọn, không cần gọi API.
        var matchedLabel = Array.from(container.querySelectorAll('label')).find(function (lb) {
            return lb.textContent.trim().replace(/^#\s*/, '').toLowerCase() === name.toLowerCase();
        });
        if (matchedLabel) {
            document.getElementById(matchedLabel.getAttribute('for')).checked = true;
            input.value = '';
            showMessage('Tag đã có sẵn, đã chọn cho bạn.', 'muted');
            return;
        }

        addBtn.disabled = true;
        fetch('/tags/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name })
        })
        .then(function (res) {
            return res.json().then(function (data) {
                if (!res.ok) throw new Error(data.error || 'Có lỗi xảy ra');
                return data;
            });
        })
        .then(function (tag) {
            addTagCheckbox(tag, true);
            input.value = '';
            showMessage(
                tag.created ? 'Đã tạo tag mới và chọn cho bạn.' : 'Tag đã có sẵn, đã chọn cho bạn.',
                'success'
            );
        })
        .catch(function (err) {
            showMessage(err.message, 'danger');
        })
        .finally(function () {
            addBtn.disabled = false;
        });
    }

    addBtn.addEventListener('click', handleAddTag);
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleAddTag();
        }
    });
});