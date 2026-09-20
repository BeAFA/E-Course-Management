
// 1. Cập nhật số câu đã chọn đáp án
function updateProgress() {
    const checkedRadios = document.querySelectorAll('input[type="radio"]:checked');
    const countSpan = document.getElementById('answeredCount');
    if (countSpan) {
        countSpan.textContent = checkedRadios.length;
    }
}

// 2. Xóa lựa chọn cho câu hỏi được chỉ định
function clearChoice(groupName) {
    const radios = document.getElementsByName(groupName);
    for (let r of radios) {
        r.checked = false;
    }
    updateProgress();
}

// 3. Hộp thoại xác nhận trước khi nộp bài
function confirmSubmit() {
    const examForm = document.getElementById('examForm');
    const totalQuestions = examForm ? parseInt(examForm.dataset.totalQuestions || '0', 10) : 0;
    const checkedRadios = document.querySelectorAll('input[type="radio"]:checked');
    
    if (totalQuestions > 0 && checkedRadios.length < totalQuestions) {
        return confirm(`Bạn mới làm được ${checkedRadios.length}/${totalQuestions} câu hỏi. Bạn có chắc chắn muốn nộp bài ngay không?`);
    }
    return confirm('Bạn có chắc chắn muốn nộp bài thi?');
}

// 4. Khởi tạo đồng hồ đếm ngược và gắn sự kiện khi trang sẵn sàng
document.addEventListener('DOMContentLoaded', function () {
    // Cập nhật tiến độ ban đầu
    updateProgress();

    // Đồng hồ đếm ngược 30 phút
    let totalSeconds = 30 * 60;
    const timeDisplay = document.getElementById('timeDisplay');
    const examForm = document.getElementById('examForm');

    if (timeDisplay && examForm) {
        const timerInterval = setInterval(() => {
            if (totalSeconds <= 0) {
                clearInterval(timerInterval);
                alert("Đã hết thời gian làm bài! Hệ thống sẽ tự động nộp bài thi.");
                examForm.submit();
                return;
            }
            totalSeconds--;
            const mins = Math.floor(totalSeconds / 60);
            const secs = totalSeconds % 60;
            timeDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }, 1000);
    }
});