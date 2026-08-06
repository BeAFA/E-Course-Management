const videoInput = document.getElementById("video");
const newVideoPreview = document.getElementById("new-video-wrapper"); // Đổi tên biến cho chuẩn
const newVideo = document.getElementById("new-video-thumb");
const currentVideoPreview = document.getElementById("current-video-preview");

let currentObjectUrl = null;

videoInput.addEventListener("change", function () {
    const file = this.files[0];

    // Xóa bộ nhớ cache của URL cũ nếu có để tránh rò rỉ bộ nhớ
    if (currentObjectUrl) {
        URL.revokeObjectURL(currentObjectUrl);
        currentObjectUrl = null;
    }

    if (file) {
        // Tạo URL giả lập cho file vừa chọn
        currentObjectUrl = URL.createObjectURL(file);

        // Gán URL cho video player
        newVideo.src = currentObjectUrl;
        newVideo.load();

        // Hiển thị khung video mới
        newVideoPreview.style.display = "block";

        // Ẩn khung video hiện tại (nếu đang ở chế độ edit và có video cũ)
//        if (currentVideoPreview) {
//            currentVideoPreview.style.display = "none";
//        }
    } else {
        // Nếu người dùng nhấn "Cancel" trong hộp thoại chọn file
        newVideo.removeAttribute("src");
        newVideo.load();

        // Ẩn khung video mới
        newVideoPreview.style.display = "none";

        // Hiển thị lại video cũ (nếu có)
        if (currentVideoPreview) {
            currentVideoPreview.style.display = "block";
        }
    }
});