document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('form').addEventListener('submit', function (e) {
        const checkedTags = document.querySelectorAll('input[name="tag_ids"]:checked');
        if (checkedTags.length === 0) {
            e.preventDefault();
            alert('Vui lòng chọn ít nhất 1 thẻ Tag cho khóa học trước khi lưu!');
        }
    });
});