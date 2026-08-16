/**
 * CareFirst Dental Clinic - AI Patient Assistant ("Ask CareFirst")
 * Vanilla JS Client Engine
 */

(function() {
  'use strict';

  // State
  let sessionId = localStorage.getItem('carefirst_chat_session') || generateUUID();
  localStorage.setItem('carefirst_chat_session', sessionId);

  let isOpen = false;
  let isSending = false;

  // DOM Elements
  const launcher = document.getElementById('cfChatLauncher');
  const panel = document.getElementById('cfChatPanel');
  const closeBtn = document.getElementById('cfChatClose');
  const body = document.getElementById('cfChatBody');
  const input = document.getElementById('cfChatInput');
  const sendBtn = document.getElementById('cfChatSend');
  const quickActionsContainer = document.getElementById('cfChatQuickActions');
  const typingIndicator = document.getElementById('cfChatTyping');

  function generateUUID() {
    return 'cf-chat-' + Math.random().toString(36).substring(2, 15) + '-' + Date.now().toString(36);
  }

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

  // Safe Markdown parser for basic formatting
  function renderMarkdown(text) {
    if (!text) return '';
    let escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Bold
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic
    escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Inline code
    escaped = escaped.replace(/`(.*?)`/g, '<code>$1</code>');
    // Links
    escaped = escaped.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    // Line breaks
    escaped = escaped.replace(/\n/g, '<br>');

    return escaped;
  }

  function scrollToBottom() {
    if (body) {
      body.scrollTop = body.scrollHeight;
    }
  }

  function appendMessage(role, content, timeStr, cards, quickActions, msgId) {
    if (!body) return;

    const row = document.createElement('div');
    row.className = `cf-chat-msg-row ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'cf-chat-msg-bubble';
    bubble.innerHTML = renderMarkdown(content);

    // Render Cards if any
    if (cards && Array.isArray(cards)) {
      cards.forEach(card => {
        const cardEl = document.createElement('div');
        cardEl.className = 'cf-chat-card';

        if (card.type === 'treatment_card') {
          cardEl.innerHTML = `
            <div class="cf-chat-card-title">${card.name}</div>
            <div class="cf-chat-card-price">Starting from ${card.starting_price}</div>
            <a href="${card.url}" class="cf-chat-card-btn" target="_blank">View Treatment Details →</a>
          `;
        } else if (card.type === 'pricing_card') {
          let itemsHtml = '';
          if (card.items && card.items.length) {
            itemsHtml = card.items.map(i => `<li class="d-flex justify-content-between"><span>${i.name}</span><strong>${i.price}</strong></li>`).join('');
          }
          cardEl.innerHTML = `
            <div class="cf-chat-card-title">${card.treatment} Price List</div>
            <ul class="list-unstyled mb-2 small text-muted">${itemsHtml}</ul>
            <small class="text-muted d-block mb-2">${card.note || ''}</small>
            <button class="cf-chat-card-btn w-100 border-0" onclick="window.careFirstChat.startAppointment('${card.treatment}')">Book Consultation</button>
          `;
        } else if (card.type === 'contact_card' || card.type === 'emergency_contact') {
          cardEl.innerHTML = `
            <div class="cf-chat-card-title text-danger">${card.title || 'Contact CareFirst'}</div>
            <p class="small mb-2 text-muted">${card.address || 'Shankhamul-31, Kathmandu'}</p>
            <div class="d-flex gap-2">
              <a href="tel:${card.phone}" class="cf-chat-card-btn flex-fill">📞 Call ${card.phone}</a>
              <a href="${card.whatsapp_url}" target="_blank" class="cf-chat-card-btn whatsapp flex-fill">WhatsApp</a>
            </div>
          `;
        } else if (card.type === 'appointment_launcher') {
          cardEl.innerHTML = `
            <div class="cf-chat-card-title">${card.title}</div>
            <button class="cf-chat-card-btn w-100 border-0" onclick="window.careFirstChat.startAppointment('${card.treatment}')">Open Appointment Form</button>
          `;
        }
        bubble.appendChild(cardEl);
      });
    }

    // Feedback row for assistant messages
    if (role === 'assistant' && msgId) {
      const feedbackWrap = document.createElement('div');
      feedbackWrap.className = 'd-flex align-items-center justify-content-between mt-2 pt-1 border-top';
      feedbackWrap.style.borderColor = '#F1F5F9';
      feedbackWrap.innerHTML = `
        <span style="font-size:0.7rem; color:#94A3B8;">Was this helpful?</span>
        <div class="d-flex gap-2">
          <button class="btn btn-sm p-0 border-0 shadow-none text-muted" style="font-size:0.75rem;" onclick="window.careFirstChat.sendFeedback(${msgId}, 'positive', this)">👍 Yes</button>
          <button class="btn btn-sm p-0 border-0 shadow-none text-muted" style="font-size:0.75rem;" onclick="window.careFirstChat.sendFeedback(${msgId}, 'negative', this)">👎 No</button>
        </div>
      `;
      bubble.appendChild(feedbackWrap);
    }

    const timeEl = document.createElement('div');
    timeEl.className = 'cf-chat-msg-time';
    timeEl.textContent = timeStr || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    bubble.appendChild(timeEl);

    row.appendChild(bubble);
    body.appendChild(row);
    scrollToBottom();

    // Render Quick Actions
    renderQuickActions(quickActions);
  }

  function renderQuickActions(actions) {
    if (!quickActionsContainer) return;
    quickActionsContainer.innerHTML = '';
    if (!actions || !actions.length) {
      quickActionsContainer.style.display = 'none';
      return;
    }

    quickActionsContainer.style.display = 'flex';
    actions.forEach(actionText => {
      const chip = document.createElement('button');
      chip.className = 'cf-chat-chip';
      chip.textContent = actionText;
      chip.onclick = () => {
        if (actionText === 'Book Appointment' || actionText.startsWith('Book')) {
          startAppointmentModal();
        } else if (actionText === 'Call Clinic' || actionText.startsWith('Call')) {
          window.location.href = 'tel:+9779807464136';
        } else if (actionText.includes('WhatsApp')) {
          window.open('https://wa.me/9779807464136', '_blank');
        } else {
          sendMessage(actionText);
        }
      };
      quickActionsContainer.appendChild(chip);
    });
  }

  function showTyping(show) {
    if (typingIndicator) {
      typingIndicator.style.display = show ? 'flex' : 'none';
      if (show) scrollToBottom();
    }
  }

  async function sendMessage(text) {
    const msg = text || (input ? input.value.trim() : '');
    if (!msg || isSending) return;

    if (input) input.value = '';
    isSending = true;
    if (sendBtn) sendBtn.disabled = true;

    // Append user message immediately
    appendMessage('user', msg);
    showTyping(true);

    const currentPage = window.location.pathname;
    const currentTreatment = document.body.getAttribute('data-treatment-slug') || '';

    try {
      const response = await fetch('/api/chat/message/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: msg,
          current_page: currentPage,
          current_treatment: currentTreatment
        })
      });

      const res = await response.json();
      showTyping(false);

      if (res.success && res.data) {
        appendMessage(
          'assistant',
          res.data.content,
          res.data.created_at,
          res.data.cards,
          res.data.quick_actions,
          res.data.id
        );
      } else {
        appendMessage(
          'assistant',
          res.error || "I'm having a little trouble connecting right now. You can call CareFirst directly at **+977 980-7464136** or chat with us on WhatsApp.",
          null,
          [{
            type: 'contact_card',
            phone: '+977 980-7464136',
            whatsapp_url: 'https://wa.me/9779807464136'
          }],
          ["Call Clinic", "WhatsApp CareFirst", "Try Again"]
        );
      }
    } catch (err) {
      showTyping(false);
      appendMessage(
        'assistant',
        "Our connection had a momentary hiccup. Please call CareFirst directly at **+977 980-7464136** or message us on WhatsApp.",
        null,
        [{
          type: 'contact_card',
          phone: '+977 980-7464136',
          whatsapp_url: 'https://wa.me/9779807464136'
        }]
      );
    } finally {
      isSending = false;
      if (sendBtn) sendBtn.disabled = false;
      if (input) input.focus();
    }
  }

  async function loadHistory() {
    try {
      const resp = await fetch(`/api/chat/history/?session_id=${encodeURIComponent(sessionId)}`);
      const data = await resp.json();
      if (data.success && data.messages && data.messages.length > 0) {
        if (body) body.innerHTML = '';
        data.messages.forEach(m => {
          appendMessage(m.role, m.content, m.created_at, m.cards, m.quick_actions, m.id);
        });
      } else {
        // Initial welcome message
        const currentTreatment = document.body.getAttribute('data-treatment-slug') || '';
        let welcome = "Namaste! I'm **Ask CareFirst**, your dental assistant.\n\nI can help you explore our treatments, check current prices, estimate costs, or book an appointment.";
        let actions = ["Our Treatments", "Treatment Prices", "Book Appointment", "Opening Hours & Location"];
        
        if (currentTreatment) {
          welcome = `Namaste! You're currently viewing **${currentTreatment.replace(/-/g, ' ').toUpperCase()}**.\n\nHow can I assist you with this treatment?`;
          actions = ["Pricing for this", "Procedure Steps", "Book Appointment", "Other Treatments"];
        }

        appendMessage('assistant', welcome, null, null, actions);
      }
    } catch (e) {
      console.warn("Could not load chat history", e);
    }
  }

  function toggleChat(openState) {
    isOpen = typeof openState === 'boolean' ? openState : !isOpen;
    if (panel) {
      if (isOpen) {
        panel.classList.add('active');
        if (launcher) launcher.classList.add('is-open');
        if (input) input.focus();
        loadHistory();
      } else {
        panel.classList.remove('active');
        if (launcher) launcher.classList.remove('is-open');
      }
    }
  }

  // Appointment Modal Helper
  function startAppointmentModal(treatmentName) {
    const defaultTreatment = treatmentName || document.body.getAttribute('data-treatment-slug') || 'General Check-up';
    const formHtml = `
      <div class="p-3 bg-white rounded-3 border">
        <h6 class="fw-bold mb-2 text-primary"><i class="bi bi-calendar-check me-1"></i> Quick Appointment Request</h6>
        <div class="mb-2">
          <input type="text" id="cfQuickName" class="form-control form-control-sm" placeholder="Your Full Name *" required>
        </div>
        <div class="mb-2">
          <input type="tel" id="cfQuickPhone" class="form-control form-control-sm" placeholder="Phone Number (e.g. 98XXXXXXXX) *" required>
        </div>
        <div class="mb-2">
          <input type="date" id="cfQuickDate" class="form-control form-control-sm" value="${new Date(Date.now() + 86400000).toISOString().split('T')[0]}">
        </div>
        <button class="btn btn-primary btn-sm w-100 fw-bold" onclick="window.careFirstChat.submitAppointmentForm('${defaultTreatment}')">Submit Appointment Request</button>
      </div>
    `;

    appendMessage('assistant', `Please fill out your preferred details below to book for **${defaultTreatment}**:`, null, null, []);
    const row = document.createElement('div');
    row.className = 'cf-chat-msg-row assistant';
    const bubble = document.createElement('div');
    bubble.className = 'cf-chat-msg-bubble w-100';
    bubble.innerHTML = formHtml;
    row.appendChild(bubble);
    body.appendChild(row);
    scrollToBottom();
  }

  // Event Listeners
  if (launcher) launcher.addEventListener('click', () => toggleChat());
  if (closeBtn) closeBtn.addEventListener('click', () => toggleChat(false));

  if (sendBtn) sendBtn.addEventListener('click', () => sendMessage());
  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  // Global window API for buttons
  window.careFirstChat = {
    open: (treatmentSlug) => {
      toggleChat(true);
      if (treatmentSlug) {
        sendMessage(`Tell me about ${treatmentSlug.replace(/-/g, ' ')}`);
      }
    },
    close: () => toggleChat(false),
    startAppointment: (treatment) => startAppointmentModal(treatment),
    submitAppointmentForm: async (treatment) => {
      const nameInput = document.getElementById('cfQuickName');
      const phoneInput = document.getElementById('cfQuickPhone');
      const dateInput = document.getElementById('cfQuickDate');

      const name = nameInput ? nameInput.value.trim() : '';
      const phone = phoneInput ? phoneInput.value.trim() : '';
      const date = dateInput ? dateInput.value : '';

      if (!name || !phone) {
        alert("Please enter both your name and contact phone number.");
        return;
      }

      showTyping(true);
      try {
        const resp = await fetch('/api/chat/appointment/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || ''
          },
          body: JSON.stringify({
            session_id: sessionId,
            full_name: name,
            phone: phone,
            preferred_date: date,
            treatment: treatment
          })
        });

        const res = await resp.json();
        showTyping(false);

        if (res.success) {
          appendMessage('assistant', `✅ **Appointment Request Submitted!**\n\nThank you, **${res.full_name}**. We have logged your request for **${res.treatment}** on **${res.preferred_date}**.\n\nOur clinic team will call or WhatsApp **${res.phone}** to confirm your slot.`);
        } else {
          appendMessage('assistant', `❌ ${res.error || 'Failed to submit appointment request. Please call us directly.'}`);
        }
      } catch (e) {
        showTyping(false);
        appendMessage('assistant', "Could not submit your request. Please call **+977 980-7464136**.");
      }
    },
    sendFeedback: async (msgId, rating, btnEl) => {
      try {
        await fetch('/api/chat/feedback/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || ''
          },
          body: JSON.stringify({
            session_id: sessionId,
            message_id: msgId,
            rating: rating
          })
        });
        if (btnEl && btnEl.parentElement) {
          btnEl.parentElement.innerHTML = '<span class="text-success fw-bold" style="font-size:0.75rem;">Thanks!</span>';
        }
      } catch (e) {}
    }
  };

})();
