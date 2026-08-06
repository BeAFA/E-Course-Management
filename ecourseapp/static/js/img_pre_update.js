const imgInput = document.getElementById('img');
    const newPreview = document.getElementById('new-img-preview');
    const newThumb = document.getElementById('new-img-thumb');
    const currentPreview = document.getElementById('current-img-preview');

    imgInput.addEventListener('change', function () {
        const file = this.files[0];

        if (file) {
            const objectUrl = URL.createObjectURL(file);
            newThumb.src = objectUrl;
            newPreview.style.display = 'flex';

            // Ẩn ảnh cũ đi để tập trung vào ảnh mới (tuỳ chọn)
            if (currentPreview) {
                currentPreview.style.display = 'none';
            }
        } else {
            newPreview.style.display = 'none';
            if (currentPreview) {
                currentPreview.style.display = 'flex';
            }
        }
    });