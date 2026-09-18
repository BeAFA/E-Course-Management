document.addEventListener('DOMContentLoaded', () => {
    // 1. Tự động cập nhật thanh tiến độ từ data-progress do Backend truyền xuống
    const progressFill = document.getElementById('courseProgressFill');
    const progressText = document.getElementById('courseProgressText');

    if (progressFill) {
        let progressVal = progressFill.getAttribute('data-progress');
        // Tránh giá trị undefined, ép kiểu an toàn
        progressVal = (progressVal !== null && progressVal !== '') ? parseInt(progressVal, 10) : 0;
        if (isNaN(progressVal)) progressVal = 0;

        progressFill.style.width = progressVal + '%';
        if (progressText) {
            progressText.textContent = progressVal + '%';
        }
    }

    // 2. Xử lý đóng/mở Accordion (Bài giảng / Bài kiểm tra)
    const moduleHeaders = document.querySelectorAll('[data-toggle="accordion"]');
    moduleHeaders.forEach(header => {
        header.addEventListener('click', (e) => {
            // Không kích hoạt toggle khi người dùng bấm vào các nút link/button bên trong header
            if (e.target.closest('a, button, form')) {
                return;
            }

            const card = header.closest('.module-card');
            if (card) {
                card.classList.toggle('collapsed');
            }
        });
    });

    // 3. Tìm kiếm bài giảng/bài thi theo từ khóa
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        const lessonItems = document.querySelectorAll('.lesson-item');
        searchInput.addEventListener('input', (e) => {
            const keyword = e.target.value.toLowerCase().trim();
            lessonItems.forEach(item => {
                const titleEl = item.querySelector('.lesson-link');
                if (titleEl) {
                    const title = titleEl.textContent.toLowerCase();
                    item.style.display = title.includes(keyword) ? 'flex' : 'none';
                }
            });
        });
    }

    // 4. Nút Trợ lý AI (Mở modal chat hoặc hành động tương ứng)
    const btnAiChat = document.getElementById('btnAiChat');
    if (btnAiChat) {
        btnAiChat.addEventListener('click', () => {
            const aiQuery = prompt('AI Assistant: Bạn cần giải đáp thắc mắc gì về khóa học này?');
            if (aiQuery && aiQuery.trim() !== '') {
                alert(`Hệ thống đang xử lý câu hỏi: "${aiQuery}"...`);
            }
        });
    }
});