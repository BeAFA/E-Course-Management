document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".ckeditor").forEach(editor => {
        ClassicEditor
            .create(editor)
            .catch(error => console.error(error));
    });
});