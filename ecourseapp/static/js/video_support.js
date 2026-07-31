function initVideoControls(videoId) {
    const video = document.getElementById(videoId);

    if (!video) {
        console.error("Không tìm thấy video");
        return;
    }

    function seek(seconds) {
        video.currentTime = Math.max(0, Math.min(video.duration, video.currentTime + seconds));
    }

    video.addEventListener('keydown', function (e) {
        if (e.code === 'ArrowRight') {
            e.preventDefault();
            seek(10);
        } else if (e.code === 'ArrowLeft') {
            e.preventDefault();
            seek(-10);
        }
    });
}