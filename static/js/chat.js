/**
 * SkillConnect - Real-Time Chat Polling Controller (Vanilla JS)
 * No WebSockets/Node.js required - clean AJAX polling with Django backend
 */

document.addEventListener('DOMContentLoaded', () => {
  const chatMessages = document.getElementById('chatMessages');
  const chatForm = document.getElementById('chatForm');
  const messageInput = document.getElementById('messageInput');

  if (!chatMessages || !chatForm) return;

  const conversationId = chatForm.dataset.conversationId;
  let lastMessageId = parseInt(chatForm.dataset.lastMessageId || '0', 10);

  // Auto-scroll to bottom
  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  scrollToBottom();

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');

  function appendMessage(msg) {
    const bubble = document.createElement('div');
    bubble.className = `msg-bubble ${msg.is_me ? 'sent' : 'received'}`;
    bubble.innerHTML = `
      <div class="msg-content">${escapeHTML(msg.content)}</div>
      <div class="msg-time">${msg.created_at}</div>
    `;
    chatMessages.appendChild(bubble);
    scrollToBottom();
  }

  function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
      tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
      }[tag] || tag)
    );
  }

  // Send message
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const content = messageInput.value.trim();
    if (!content) return;

    messageInput.value = '';

    const formData = new FormData();
    formData.append('content', content);

    try {
      const res = await fetch(`/chat/${conversationId}/send/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        if (data.success) {
          lastMessageId = Math.max(lastMessageId, data.message.id);
          appendMessage(data.message);
        }
      }
    } catch (err) {
      console.error('Send message error:', err);
    }
  });

  // Polling for incoming messages every 3 seconds
  setInterval(async () => {
    try {
      const res = await fetch(`/chat/${conversationId}/poll/?last_id=${lastMessageId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.messages && data.messages.length > 0) {
          data.messages.forEach(msg => {
            if (!msg.is_me) { // Avoid duplicating locally appended sent messages
              appendMessage(msg);
            }
            lastMessageId = Math.max(lastMessageId, msg.id);
          });
        }
      }
    } catch (err) {
      // Quiet fail during network blips
    }
  }, 3000);
});
