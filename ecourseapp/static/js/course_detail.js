document.addEventListener('DOMContentLoaded', () => {
    // 1. Tự động cập nhật thanh tiến độ từ data-progress
    const progressFill = document.getElementById('courseProgressFill');
    if (progressFill) {
        const progressVal = progressFill.getAttribute('data-progress') || '35';
        progressFill.style.width = progressVal + '%';
    }

    // 2. Xử lý đóng/mở Accordion (Bài giảng / Bài kiểm tra)
    const moduleHeaders = document.querySelectorAll('[data-toggle="accordion"]');
    moduleHeaders.forEach(header => {
        header.addEventListener('click', () => {
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

    // 4. Hỏi đáp với giảng viên
    const btnAskTeacher = document.getElementById('btnAskTeacher');
    if (btnAskTeacher) {
        btnAskTeacher.addEventListener('click', () => {
            const question = prompt('Nhập câu hỏi của bạn gửi đến giảng viên:');
            if (question && question.trim() !== '') {
                alert('Câu hỏi của bạn đã được gửi tới giảng viên thành công!');
            }
        });
    }

    // 5. Trợ lý AI
    const btnAiChat = document.getElementById('btnAiChat');
    if (btnAiChat) {
        btnAiChat.addEventListener('click', () => {
            const aiQuery = prompt('AI Assistant: Bạn cần hỏi gì về khóa học này?');
            if (aiQuery && aiQuery.trim() !== '') {
                alert(`AI đang xử lý câu hỏi: "${aiQuery}"...`);
            }
        });
    }

    // 6. Nút Đăng xuất
    const btnLogout = document.getElementById('btnLogout');
    if (btnLogout) {
        btnLogout.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm('Bạn có chắc chắn muốn đăng xuất không?')) {
                window.location.href = '/logout';
            }
        });
    }
});