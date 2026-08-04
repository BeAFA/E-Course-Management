document.addEventListener('DOMContentLoaded', () => {
    const moduleHeaders = document.querySelectorAll('[data-toggle="accordion"]');
    moduleHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const card = header.closest('.module-card');
            card.classList.toggle('collapsed');
        });
    });

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

//    const lessonLinks = document.querySelectorAll('.lesson-link');
//    lessonLinks.forEach(link => {
//        link.addEventListener('click', (e) => {
//            e.preventDefault();
//            const title = link.getAttribute('data-title') || link.textContent.trim();
//            const type = link.getAttribute('data-type');
//
//            if (type === 'video') {
//                alert(`Đang mở video bài giảng: "${title}"`);
//            } else if (type === 'quiz') {
//                alert(`Bắt đầu làm: "${title}"`);
//            } else if (type === 'essay') {
//                alert(`Khu vực nộp bài cho: "${title}"`);
//            } else if (type === 'exam') {
//                if (confirm(`Bạn chuẩn bị làm "${title}". Thời gian sẽ được tính ngay khi bắt đầu. Tiếp tục?`)) {
//                    alert('Đang tải đề thi...');
//                }
//            } else {
//                alert(`Đang mở tài liệu: "${title}"`);
//            }
//        });
//    });

    const btnAskTeacher = document.getElementById('btnAskTeacher');
    if (btnAskTeacher) {
        btnAskTeacher.addEventListener('click', () => {
            const question = prompt('Nhập câu hỏi của bạn gửi đến giảng viên:');
            if (question && question.trim() !== '') {
                alert('Câu hỏi của bạn đã được gửi tới giảng viên thành công!');
            }
        });
    }

    const btnAiChat = document.getElementById('btnAiChat');
    if (btnAiChat) {
        btnAiChat.addEventListener('click', () => {
            const aiQuery = prompt('AI Assistant: Bạn cần hỏi gì về khóa học này?');
            if (aiQuery && aiQuery.trim() !== '') {
                alert(`AI đang xử lý câu hỏi: "${aiQuery}"...`);
            }
        });
    }

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