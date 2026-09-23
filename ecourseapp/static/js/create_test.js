document.addEventListener('DOMContentLoaded', function () {
    const questionsContainer = document.getElementById('questions-container');
    const addQuestionBtn = document.getElementById('add-question-btn');

    // Tự động đếm số câu hỏi ban đầu trên trang (hỗ trợ trường hợp nhân bản)
    let questionCount = questionsContainer ? questionsContainer.querySelectorAll('.question-block').length : 1;

    if (addQuestionBtn && questionsContainer) {
        addQuestionBtn.addEventListener('click', function () {
            const qIndex = questionCount;

            const qHTML = `
                <div class="test-card question-block" data-question-index="${qIndex}">
                    <div class="block-title">
                        <span class="q-badge">Câu hỏi ${qIndex + 1}</span>
                        <button type="button" class="btn-del-q remove-question-btn">
                            <i class="fa-solid fa-trash-can me-1"></i> Xóa câu hỏi
                        </button>
                    </div>
                    <div class="form-group-custom">
                        <label class="form-label-custom">Nội dung câu hỏi (*)</label>
                        <input type="text" name="question_content[]" class="form-control-custom" placeholder="Nhập nội dung câu hỏi..." required>
                    </div>

                    <label class="form-label-custom" style="margin-top: 14px;">Các lựa chọn đáp án:</label>
                    <div class="choices-container">
                        <div class="choice-item-row">
                            <label class="radio-btn-wrapper">
                                <input type="radio" name="correct_choice_${qIndex}" value="0" checked>
                                <span>Đáp án Đúng</span>
                            </label>
                            <input type="text" name="choice_answer_${qIndex}[]" class="form-control-custom" placeholder="Đáp án A" required>
                            <button type="button" class="btn-delete-choice" title="Xóa đáp án"><i class="fa-solid fa-xmark"></i></button>
                        </div>
                        <div class="choice-item-row">
                            <label class="radio-btn-wrapper">
                                <input type="radio" name="correct_choice_${qIndex}" value="1">
                                <span>Đáp án Đúng</span>
                            </label>
                            <input type="text" name="choice_answer_${qIndex}[]" class="form-control-custom" placeholder="Đáp án B" required>
                            <button type="button" class="btn-delete-choice" title="Xóa đáp án"><i class="fa-solid fa-xmark"></i></button>
                        </div>
                    </div>
                    <button type="button" class="btn-add-choice-dashed">+ Thêm đáp án khác</button>
                </div>
            `;
            questionsContainer.insertAdjacentHTML('beforeend', qHTML);
            questionCount++;
        });

        questionsContainer.addEventListener('click', function (e) {
            // Thêm đáp án
            const addChoiceBtn = e.target.closest('.btn-add-choice-dashed');
            if (addChoiceBtn) {
                const qBlock = addChoiceBtn.closest('.question-block');
                const qIndex = qBlock.getAttribute('data-question-index');
                const choicesContainer = qBlock.querySelector('.choices-container');
                const choiceIndex = choicesContainer.children.length;

                const choiceHTML = `
                    <div class="choice-item-row">
                        <label class="radio-btn-wrapper">
                            <input type="radio" name="correct_choice_${qIndex}" value="${choiceIndex}">
                            <span>Đáp án Đúng</span>
                        </label>
                        <input type="text" name="choice_answer_${qIndex}[]" class="form-control-custom" placeholder="Đáp án mới" required>
                        <button type="button" class="btn-delete-choice" title="Xóa đáp án"><i class="fa-solid fa-xmark"></i></button>
                    </div>
                `;
                choicesContainer.insertAdjacentHTML('beforeend', choiceHTML);
            }

            // Xóa đáp án
            const removeChoiceBtn = e.target.closest('.btn-delete-choice');
            if (removeChoiceBtn) {
                const choicesContainer = removeChoiceBtn.closest('.choices-container');
                if (choicesContainer.children.length > 2) {
                    removeChoiceBtn.closest('.choice-item-row').remove();
                    
                    const qBlock = choicesContainer.closest('.question-block');
                    const qIndex = qBlock.getAttribute('data-question-index');
                    Array.from(choicesContainer.children).forEach((row, idx) => {
                        const radio = row.querySelector('input[type="radio"]');
                        if (radio) radio.value = idx;
                    });
                } else {
                    alert('Mỗi câu hỏi phải giữ ít nhất 2 đáp án!');
                }
            }

            // Xóa câu hỏi
            const removeQuestionBtn = e.target.closest('.remove-question-btn');
            if (removeQuestionBtn) {
                removeQuestionBtn.closest('.question-block').remove();
            }
        });
    }
});