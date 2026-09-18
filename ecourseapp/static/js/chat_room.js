document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    const chatBox = document.getElementById("chatBox");
    const chatForm = document.getElementById("chatForm");
    const msgInput = document.getElementById("msgInput");
    const emptyState = document.getElementById("emptyState");

    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    scrollToBottom();

    socket.emit("join_chat", { room_id: CHAT_CONFIG.roomId });

    chatForm.addEventListener("submit", (e) => {
        e.preventDefault(); 

        const content = msgInput.value.trim();
        if (content !== "") {
            socket.emit("send_message", {
                room_id: CHAT_CONFIG.roomId,
                content: content
            });

            msgInput.value = "";
            msgInput.focus();
        }
    });

    socket.on("receive_message", (data) => {
        const emptyState = document.getElementById("emptyState");
        if (emptyState) emptyState.remove();

        const isMe = (data.sender_id === CHAT_CONFIG.currentUserId);

        let avatarHtml = '';
        if (data.avatar_url && typeof data.avatar_url === 'string' && data.avatar_url.trim() !== '') {
            avatarHtml = `<div class="avatar-circle" title="${data.sender_name}">
                        <img src="${data.avatar_url}" alt="${data.sender_name}">
                      </div>`;
        } else {
            avatarHtml = `<div class="avatar-circle" title="${data.sender_name}">
                        <span>${data.avatar_text}</span>
                      </div>`;
        }
    
        const messageRow = document.createElement("div");
        messageRow.className = `message-row ${isMe ? "me" : "other"}`;

        messageRow.innerHTML = `
        ${avatarHtml}
        <div class="message-bubble-wrapper">
            <div class="message-sender">${data.sender_name}</div>
            <div class="message-bubble">${data.content}</div>
        </div>
    `;

        chatBox.appendChild(messageRow);
        chatBox.scrollTop = chatBox.scrollHeight;
    });
});