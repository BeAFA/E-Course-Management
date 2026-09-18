(function () {
  "use strict";

  /* ---------- Tham chiếu phần tử ---------- */
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('overlay');
  var menuBtn = document.getElementById('menuBtn');
  var closeSidebarBtn = document.getElementById('closeSidebarBtn');
  var newChatBtn = document.getElementById('newChatBtn');
  var historyScroll = document.getElementById('historyScroll');

  var chatScreen = document.getElementById('chatScreen');
  var chatBody = document.getElementById('chatBody');
  var messageList = document.getElementById('messageList');
  var composer = document.getElementById('composer');
  var textInput = document.getElementById('textInput');
  var sendBtn = document.getElementById('sendBtn');
  var suggestBtn = document.getElementById('suggestBtn');

  // currentRoomId = null nghĩa là "đoạn chat mới chưa có trong DB",
  // sẽ được tạo thật (POST /ai_chat/rooms) ngay khi người dùng gửi tin đầu tiên.
  var currentRoomId = null;
  var conversationStarted = false;
  var isSending = false;

  /* ---------- Sidebar mở/đóng ---------- */
  function openSidebar() { sidebar.classList.add('open'); overlay.classList.add('open'); }
  function closeSidebar() { sidebar.classList.remove('open'); overlay.classList.remove('open'); }

  menuBtn.addEventListener('click', openSidebar);
  closeSidebarBtn.addEventListener('click', closeSidebar);
  overlay.addEventListener('click', closeSidebar);

  newChatBtn.addEventListener('click', function () {
    startNewChat();
    closeSidebar();
  });

  /* ---------- Gọi API danh sách đoạn chat ---------- */
  function fetchJSON(url, options) {
    return fetch(url, options).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) throw new Error(data.error || 'Có lỗi xảy ra');
        return data;
      });
    });
  }

  function groupByDate(rooms) {
    var todayStr = new Date().toDateString();
    var groups = { today: [], older: [] };
    rooms.forEach(function (r) {
      var d = r.updated_date ? new Date(r.updated_date) : new Date();
      (d.toDateString() === todayStr ? groups.today : groups.older).push(r);
    });
    return groups;
  }

  function loadChatList() {
    return fetchJSON('/ai_chat/rooms').then(function (rooms) {
      historyScroll.innerHTML = '';
      var groups = groupByDate(rooms);

      function renderGroup(label, list) {
          if (!list.length) return;
          var wrap = document.createElement('div');
          wrap.className = 'history-group';
          var title = document.createElement('p');
          title.className = 'history-group-label';
          title.textContent = label;
          wrap.appendChild(title);

          list.forEach(function (r) {
            var item = document.createElement('div');
            item.className = 'history-item' + (r.id === currentRoomId ? ' active' : '');
            item.setAttribute('data-id', r.id);

            var titleBtn = document.createElement('button');
            titleBtn.className = 'history-item-title';
            titleBtn.textContent = r.title;
            item.appendChild(titleBtn);

            var delBtn = document.createElement('button');
            delBtn.className = 'history-delete-btn';
            delBtn.setAttribute('aria-label', 'Xóa đoạn chat');
            delBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0-1 14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2L4 6"/></svg>';
            item.appendChild(delBtn);

            wrap.appendChild(item);
          });
          historyScroll.appendChild(wrap);
        }

      renderGroup('Hôm nay', groups.today);
      renderGroup('Cũ hơn', groups.older);
    }).catch(function (err) {
      console.error('Không tải được danh sách đoạn chat:', err);
    });
  }

  // Click 1 đoạn chat cũ trong sidebar -> mở NGAY TRONG màn hình chat chính
  // (không phải màn hình chỉ-xem riêng) để có thể gửi tiếp tin nhắn.
  historyScroll.addEventListener('click', function (e) {
      var delBtn = e.target.closest('.history-delete-btn');
      if (delBtn) {
        e.stopPropagation();
        var item = delBtn.closest('.history-item');
        var roomId = parseInt(item.getAttribute('data-id'), 10);
        deleteChat(roomId, item);
        return;
      }

      var titleBtn = e.target.closest('.history-item-title');
      if (!titleBtn) return;
      var roomId = parseInt(titleBtn.closest('.history-item').getAttribute('data-id'), 10);
      openExistingChat(roomId);
      closeSidebar();
    });

    function deleteChat(roomId, itemNode) {
      if (!confirm('Xóa đoạn chat này? Hành động không thể hoàn tác.')) return;

      fetchJSON('/ai_chat/rooms/' + roomId, { method: 'DELETE' })
        .then(function () {
          itemNode.remove();
          // Nếu đang mở đúng đoạn chat vừa xóa -> quay về trạng thái "đoạn chat mới"
          if (roomId === currentRoomId) {
            startNewChat();
          }
        })
        .catch(function (err) {
          alert('Không xóa được đoạn chat: ' + err.message);
        });
    }

  function openExistingChat(roomId) {
    fetchJSON('/ai_chat/rooms/' + roomId + '/messages').then(function (data) {
      currentRoomId = roomId;
      conversationStarted = data.messages.length > 0;
      chatBody.classList.toggle('is-empty', !conversationStarted);
      messageList.innerHTML = '';
      data.messages.forEach(function (m) { messageList.appendChild(buildMessageNode(m)); });
      scrollToBottom();
      loadChatList(); // để cập nhật highlight item đang active
    }).catch(function (err) {
      alert('Không mở được đoạn chat: ' + err.message);
    });
  }

  function buildMessageNode(m) {
      var wrap = document.createElement('div');
      wrap.className = 'msg ' + (m.role === 'user' ? 'msg-user' : 'msg-ai');

      var avatar = document.createElement('div');
      avatar.className = 'msg-avatar';
      avatar.textContent = m.role === 'user' ? 'Bạn' : 'AI';

      var bubble = document.createElement('div');
      bubble.className = 'msg-bubble';
      var p = document.createElement('div');
      p.textContent = m.text;
      bubble.appendChild(p);

      if (m.courses && m.courses.length) {
        var cardsWrap = document.createElement('div');
        cardsWrap.className = 'course-cards';
        m.courses.forEach(function (c) { cardsWrap.appendChild(buildCourseCard(c)); });
        bubble.appendChild(cardsWrap);

        var viewAllBtn = document.createElement('a');
        viewAllBtn.className = 'view-all-courses-btn';
        var ids = m.courses.map(function (c) { return c.id; }).join(',');
        viewAllBtn.href = '/courses?ids=' + encodeURIComponent(ids);
        viewAllBtn.textContent = 'Xem tất cả ' + m.courses.length + ' khóa học';
        bubble.appendChild(viewAllBtn);
      }

      wrap.appendChild(avatar);
      wrap.appendChild(bubble);
      return wrap;
    }

  /* ---------- Soạn tin nhắn (auto-resize textarea) ---------- */
  var MAX_TEXTAREA_LINES = 5;

  function getTextareaMaxHeight() {
    var cs = getComputedStyle(textInput);
    var lineHeight = parseFloat(cs.lineHeight);
    if (!lineHeight || isNaN(lineHeight)) lineHeight = parseFloat(cs.fontSize) * 1.4;
    var paddingV = parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
    return Math.round(lineHeight * MAX_TEXTAREA_LINES + paddingV);
  }

  function autoResize() {
    textInput.style.height = 'auto';
    textInput.style.height = Math.min(textInput.scrollHeight, getTextareaMaxHeight()) + 'px';
  }

  textInput.addEventListener('input', function () {
    autoResize();
    sendBtn.disabled = textInput.value.trim().length === 0;
  });
  textInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  sendBtn.addEventListener('click', function () { sendMessage(); });

  suggestBtn.addEventListener('click', function () {
    sendMessage('Gợi ý cho tôi khóa học phù hợp với mục tiêu học tập của tôi');
  });

  function markConversationStarted() {
    if (conversationStarted) return;
    conversationStarted = true;
    chatBody.classList.remove('is-empty');
  }

  function startNewChat() {
    currentRoomId = null;
    conversationStarted = false;
    chatBody.classList.add('is-empty');
    messageList.innerHTML = '';
    textInput.value = '';
    autoResize();
    sendBtn.disabled = true;
    loadChatList();
  }

  /* ---------- Gửi tin nhắn (tạo phòng chat mới nếu cần, rồi gọi API) ---------- */
  function ensureRoom() {
    if (currentRoomId) return Promise.resolve(currentRoomId);
    return fetchJSON('/ai_chat/rooms', { method: 'POST' }).then(function (room) {
      currentRoomId = room.id;
      return currentRoomId;
    });
  }

  function sendMessage(presetText) {
    if (isSending) return;
    var text = (presetText !== undefined ? presetText : textInput.value).trim();
    if (!text) return;

    isSending = true;
    markConversationStarted();
    messageList.appendChild(buildMessageNode({ role: 'user', text: text }));
    textInput.value = '';
    autoResize();
    sendBtn.disabled = true;
    scrollToBottom();

    var typingNode = showTypingIndicator();

    ensureRoom()
      .then(function (roomId) {
        return fetchJSON('/ai_chat/rooms/' + roomId + '/messages', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text }),
        });
      })
      .then(function (data) {
        typingNode.remove();
        messageList.appendChild(buildMessageNode({ role: 'ai', text: data.reply, courses: data.courses }));
        scrollToBottom();
        loadChatList(); // cập nhật tiêu đề tự đặt sau tin đầu tiên + thứ tự "gần đây"
      })
      .catch(function (err) {
        typingNode.remove();
        messageList.appendChild(buildMessageNode({ role: 'ai', text: 'Lỗi: ' + err.message }));
        scrollToBottom();
      })
      .finally(function () {
        isSending = false;
      });
  }

  function showTypingIndicator() {
    var node = document.createElement('div');
    node.className = 'msg msg-ai';
    node.innerHTML = '<div class="msg-avatar">AI</div><div class="msg-bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
    messageList.appendChild(node);
    scrollToBottom();
    return node;
  }

  function scrollToBottom() {
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  /* ---------- Dựng 1 dòng tin nhắn ---------- */
  function buildMessageNode(m) {
    var wrap = document.createElement('div');
    wrap.className = 'msg ' + (m.role === 'user' ? 'msg-user' : 'msg-ai');

    var avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.textContent = m.role === 'user' ? 'Bạn' : 'AI';

    var bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    var p = document.createElement('div');
    p.textContent = m.text;
    bubble.appendChild(p);

    if (m.courses && m.courses.length) {
      var cardsWrap = document.createElement('div');
      cardsWrap.className = 'course-cards';
      m.courses.forEach(function (c) { cardsWrap.appendChild(buildCourseCard(c)); });
      bubble.appendChild(cardsWrap);
    }

    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    return wrap;
  }

  function buildCourseCard(c) {
    var card = document.createElement('div');
    card.className = 'course-card';
    card.innerHTML =
      '<div class="course-thumb">' + c.icon + '</div>' +
      '<div class="course-info">' +
      '<p class="course-name">' + c.name + '</p>' +
      '<p class="course-meta">' + c.category + '</p>' +
      '</div>' +
      '<div class="course-price">' + Number(c.price).toLocaleString('vi-VN') + ' đ</div>';
    return card;
  }

  /* ---------- Khởi động ---------- */
  loadChatList();

})();