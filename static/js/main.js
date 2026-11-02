/**
 * SkillConnect - Vanilla JavaScript Interactions
 * Pure JS - AJAX Likes, Comments, Follow, Share, Notifications, Toasts
 */

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Nav Toggle
  const mobileToggle = document.getElementById('mobileMenuToggle');
  const navLinks = document.getElementById('navLinks');
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
  }

  // Toast Container
  let toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }

  window.showToast = function(message, duration = 3000) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toastContainer.appendChild(toast);

    // Trigger reflow & show
    requestAnimationFrame(() => {
      toast.classList.add('show');
    });

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  };

  // Share Button Clipboard Copy
  document.querySelectorAll('.btn-share').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const url = btn.dataset.url || window.location.href;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(() => {
          window.showToast('Link copied to clipboard!');
        }).catch(() => {
          fallbackCopyText(url);
        });
      } else {
        fallbackCopyText(url);
      }
    });
  });

  function fallbackCopyText(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      window.showToast('Link copied to clipboard!');
    } catch (err) {
      window.showToast('Could not copy link');
    }
    document.body.removeChild(textArea);
  }

  // Helper for CSRF Token
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

  // AJAX Like Toggle
  document.querySelectorAll('.btn-like').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const postId = btn.dataset.postId;
      if (!postId) return;

      try {
        const res = await fetch(`/posts/${postId}/like/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
          }
        });
        if (res.ok) {
          const data = await res.json();
          const icon = btn.querySelector('.like-icon');
          const count = btn.querySelector('.like-count');
          if (data.liked) {
            btn.classList.add('liked');
            if (icon) icon.textContent = '♥';
          } else {
            btn.classList.remove('liked');
            if (icon) icon.textContent = '♡';
          }
          if (count) count.textContent = data.count;
        } else if (res.status === 403 || res.status === 401) {
          window.location.href = '/login/';
        }
      } catch (err) {
        console.error('Like error:', err);
      }
    });
  });

  // AJAX Follow / Unfollow Toggle
  document.querySelectorAll('.btn-follow-toggle').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const username = btn.dataset.username;
      if (!username) return;

      try {
        const res = await fetch(`/ajax/follow/${username}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
          }
        });
        if (res.ok) {
          const data = await res.json();
          if (data.is_following) {
            btn.textContent = 'Following';
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
          } else {
            btn.textContent = 'Follow';
            btn.classList.remove('btn-secondary');
            btn.classList.add('btn-primary');
          }

          const followersCounter = document.getElementById('followersCount');
          if (followersCounter) {
            followersCounter.textContent = data.followers_count;
          }
          window.showToast(data.message);
        } else if (res.status === 401 || res.status === 403) {
          window.location.href = '/login/';
        }
      } catch (err) {
        console.error('Follow error:', err);
      }
    });
  });

  // AJAX Inline Comment Submission
  document.querySelectorAll('.ajax-comment-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = form.querySelector('.comment-input');
      const content = input ? input.value.trim() : '';
      const postId = form.dataset.postId;
      if (!content || !postId) return;

      const formData = new FormData();
      formData.append('content', content);

      try {
        const res = await fetch(`/posts/${postId}/comment/`, {
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
            input.value = '';
            // Append comment to list
            const commentsList = document.getElementById(`comments-list-${postId}`);
            if (commentsList) {
              const item = document.createElement('div');
              item.className = 'comment-item';
              item.innerHTML = `
                <span class="comment-user">${data.comment.user}:</span>
                <span class="comment-text">${data.comment.content}</span>
              `;
              commentsList.appendChild(item);
              commentsList.scrollTop = commentsList.scrollHeight;
            }
            // Update comments count on card
            const countSpan = document.getElementById(`comment-count-${postId}`);
            if (countSpan) {
              countSpan.textContent = data.comments_count;
            }
          }
        }
      } catch (err) {
        console.error('Comment error:', err);
      }
    });
  });

  // Auto-dismiss Alerts after 5s
  document.querySelectorAll('.alert').forEach(alert => {
    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => alert.remove());
    }
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 6000);
  });
});
