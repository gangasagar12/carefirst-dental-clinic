/**
 * CareFirst Dental Clinic - AI Patient Assistant ("Ask CareFirst")
 * Vanilla JS Client Engine
 */

(function() {
  'use strict';

  // State
  // State & Persistent Storage
  let sessionId = localStorage.getItem('carefirst_chat_session');
  if (!sessionId) {
    sessionId = generateUUID();
    localStorage.setItem('carefirst_chat_session', sessionId);
  }

  let isOpen = localStorage.getItem('carefirst_chat_open') === 'true';
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

  function getLocalHistory() {
    try {
      return JSON.parse(localStorage.getItem('cf_chat_msgs_' + sessionId) || '[]');
    } catch (e) {
      return [];
    }
  }

  function setLocalHistory(msgs) {
    try {
      localStorage.setItem('cf_chat_msgs_' + sessionId, JSON.stringify(msgs || []));
    } catch (e) {}
  }

  function saveLocalMessage(msg) {
    try {
      const list = getLocalHistory();
      // Avoid duplicate by id or timestamp/content
      const exists = list.some(m => (m.id && m.id === msg.id) || (m.role === msg.role && m.content === msg.content && m.created_at === msg.created_at));
      if (!exists) {
        list.push(msg);
        if (list.length > 50) list.shift();
        setLocalHistory(list);
      }
    } catch (e) {}
  }

  function cleanLatexAndSymbols(text) {
    if (!text) return '';
    return text
      // Common LaTeX arrows and symbols
      .replace(/\\(?:Longrightarrow|rightarrow|to)/g, ' ➔ ')
      .replace(/\\(?:Longleftrightarrow|iff)/g, ' ⟺ ')
      .replace(/\\times/g, ' × ')
      .replace(/\\approx/g, ' ≈ ')
      .replace(/\\pm/g, ' ± ')
      .replace(/\\leq/g, ' ≤ ')
      .replace(/\\geq/g, ' ≥ ')
      .replace(/\\neq/g, ' ≠ ')
      .replace(/\\cdot/g, ' · ')
      .replace(/\\quad|\\qquad|\\;|\\,|\\!/g, ' ')
      // LaTeX structural markup removal
      .replace(/\\left\s*([\[\(\{])/g, '$1')
      .replace(/\\right\s*([\]\)\}])/g, '$1')
      .replace(/\\begin\{array\}\{[^}]*\}|\\end\{array\}/g, '')
      .replace(/\\begin\{matrix\}|\\end\{matrix\}/g, '')
      .replace(/\\begin\{pmatrix\}|\\end\{pmatrix\}/g, '')
      .replace(/\\begin\{bmatrix\}|\\end\{bmatrix\}/g, '')
      .replace(/\\frac\{([^}]+)\}\{([^}]+)\}/g, '$1/$2')
      .replace(/\\text\{([^}]+)\}/g, '$1')
      .replace(/\\textbf\{([^}]+)\}/g, '**$1**')
      .replace(/\\textit\{([^}]+)\}/g, '*$1*')
      .replace(/\\\((.*?)\\\)/g, '$1')
      .replace(/\\\[(.*?)\\\]/g, '$1')
      .replace(/\\([a-zA-Z])/g, '$1');
  }

  function formatTable(rows) {
    if (!rows || rows.length === 0) return '';
    let html = '<div class="cf-md-table-wrap"><table class="cf-md-table">';
    let isHeader = true;

    for (let r = 0; r < rows.length; r++) {
      let cells = rows[r].split('|').slice(1, -1).map(c => c.trim());
      if (isHeader) {
        html += '<thead><tr>';
        cells.forEach(c => {
          html += `<th>${c}</th>`;
        });
        html += '</tr></thead><tbody>';
        isHeader = false;
      } else {
        html += '<tr>';
        cells.forEach(c => {
          html += `<td>${c}</td>`;
        });
        html += '</tr>';
      }
    }
    html += '</tbody></table></div>';
    return html;
  }

  // Safe & Rich Markdown parser for elegant ChatGPT-style formatting
  function renderMarkdown(rawText) {
    if (!rawText) return '';

    let text = cleanLatexAndSymbols(rawText);

    // Escape HTML special characters
    let escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // 1. Code blocks (```code```)
    escaped = escaped.replace(/```([a-zA-Z0-9]*)\n?([\s\S]*?)```/g, (match, lang, code) => {
      return `<pre class="cf-md-code-block"><code>${code.trim()}</code></pre>`;
    });

    // 2. Multi-line Tables (| col1 | col2 |)
    const lines = escaped.split('\n');
    let inTable = false;
    let tableRows = [];
    let processedLines = [];

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i].trim();
      if (line.startsWith('|') && line.endsWith('|')) {
        if (!inTable) {
          inTable = true;
          tableRows = [];
        }
        if (/^\|(\s*:?-+:?\s*\|)+$/.test(line)) {
          continue;
        }
        tableRows.push(line);
      } else {
        if (inTable) {
          processedLines.push(formatTable(tableRows));
          inTable = false;
          tableRows = [];
        }
        processedLines.push(lines[i]);
      }
    }
    if (inTable) {
      processedLines.push(formatTable(tableRows));
    }

    escaped = processedLines.join('\n');

    // 3. Inline Pipes format: convert | **Key** | Details | into modern key-value cards
    escaped = escaped.replace(/\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|\n]+)\s*\|?/g, (match, key, val) => {
      return `<div class="cf-md-card"><div class="cf-md-card-head">${key.trim()}</div><div class="cf-md-card-body">${val.trim()}</div></div>`;
    });

    // 4. Headings (#, ##, ###, ####)
    escaped = escaped.replace(/^#{1,4}\s+(.+)$/gm, '<div class="cf-md-heading">$1</div>');

    // 5. Horizontal Rules
    escaped = escaped.replace(/^(\-{3,}|\_{3,}|\*{3,})$/gm, '<hr class="cf-md-hr">');

    // 6. Blockquotes (> quote)
    escaped = escaped.replace(/^>\s+(.+)$/gm, '<blockquote class="cf-md-quote">$1</blockquote>');

    // 7. Strong / Bold (**text**)
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong class="cf-md-bold">$1</strong>');

    // 8. Italic (*text*)
    escaped = escaped.replace(/(^|[^*])\*(?!\s)(.*?)(?!\s)\*(?=[^*]|$)/g, '$1<em>$2</em>');

    // 9. Inline code (`code`)
    escaped = escaped.replace(/`([^`]+)`/g, '<code class="bg-light px-1 py-0.5 rounded text-dark">$1</code>');

    // 10. Links ([text](url))
    escaped = escaped.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener" class="text-primary fw-bold text-decoration-underline">$1</a>');

    // 11. Bullet lists (- item or * item or • item)
    escaped = escaped.replace(/^[\-\*•]\s+(.+)$/gm, '<div class="cf-md-list-item">$1</div>');
    escaped = escaped.replace(/^(\d+)\.\s+(.+)$/gm, '<div class="cf-md-list-item"><strong class="me-1">$1.</strong>$2</div>');

    // 12. Paragraph separation
    const paragraphs = escaped.split(/\n\s*\n/);
    if (paragraphs.length > 1) {
      escaped = paragraphs.map(p => {
        let trimmed = p.trim();
        if (!trimmed) return '';
        if (trimmed.startsWith('<div') || trimmed.startsWith('<blockquote') || trimmed.startsWith('<pre') || trimmed.startsWith('<hr')) {
          return trimmed;
        }
        return `<p class="cf-md-p">${trimmed.replace(/\n/g, '<br>')}</p>`;
      }).join('');
    } else {
      escaped = escaped.replace(/\n/g, '<br>');
    }

    // Clean up redundant breaks around blocks
    escaped = escaped.replace(/<\/div><br>/g, '</div>');
    escaped = escaped.replace(/<br><div/g, '<div');
    escaped = escaped.replace(/<\/table><\/div><br>/g, '</table></div>');
    escaped = escaped.replace(/<br><div class="cf-md-table-wrap"/g, '<div class="cf-md-table-wrap"');

    return escaped;
  }

  function scrollToBottom() {
    if (body) {
      body.scrollTop = body.scrollHeight;
    }
  }

  function appendMessage(role, content, timeStr, cards, quickActions, msgId, saveLocal = true) {
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
    const finalTime = timeStr || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    timeEl.textContent = finalTime;
    bubble.appendChild(timeEl);

    row.appendChild(bubble);
    body.appendChild(row);
    scrollToBottom();

    // Save to local cache
    if (saveLocal) {
      saveLocalMessage({
        role: role,
        content: content,
        created_at: finalTime,
        cards: cards || [],
        quick_actions: quickActions || [],
        id: msgId || null
      });
    }

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
      const label = document.getElementById('cfTypingLabel');
      if (label && show) {
        const isNe = window.location.pathname.includes('/ne');
        label.textContent = isNe ? 'केयरफर्स्ट टाइप गर्दैछ...' : 'CareFirst is typing...';
      }
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

  async function loadHistory(forceServer = false) {
    // 1. First render from local cache instantly if available
    const localMsgs = getLocalHistory();
    if (localMsgs.length > 0 && !forceServer) {
      if (body) {
        body.innerHTML = '';
        localMsgs.forEach(m => {
          appendMessage(m.role, m.content, m.created_at, m.cards, m.quick_actions, m.id, false);
        });
      }
    }

    // 2. Sync with server in background
    try {
      const resp = await fetch(`/api/chat/history/?session_id=${encodeURIComponent(sessionId)}`);
      const data = await resp.json();
      if (data.success && data.messages && data.messages.length > 0) {
        if (body) body.innerHTML = '';
        setLocalHistory(data.messages);
        data.messages.forEach(m => {
          appendMessage(m.role, m.content, m.created_at, m.cards, m.quick_actions, m.id, false);
        });
      } else if (localMsgs.length === 0) {
        // Only show initial welcome if no history exists anywhere
        const currentTreatment = document.body.getAttribute('data-treatment-slug') || '';
        let welcome = "Namaste! I'm **Ask CareFirst**, your dental assistant.\n\nI can help you explore our treatments, check current prices, estimate costs, or book an appointment.";
        let actions = ["Our Treatments", "Treatment Prices", "Book Appointment", "Opening Hours & Location"];

        if (currentTreatment) {
          welcome = `Namaste! You're currently viewing **${currentTreatment.replace(/-/g, ' ').toUpperCase()}**.\n\nHow can I assist you with this treatment?`;
          actions = ["Pricing for this", "Procedure Steps", "Book Appointment", "Other Treatments"];
        }

        appendMessage('assistant', welcome, null, null, actions, null, true);
      }
    } catch (e) {
      console.warn("Could not sync chat history from server", e);
    }
  }

  function toggleChat(openState) {
    isOpen = typeof openState === 'boolean' ? openState : !isOpen;
    localStorage.setItem('carefirst_chat_open', isOpen ? 'true' : 'false');
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
        <div class="text-center mt-2">
          <a href="/appointment/?treatment=${encodeURIComponent(defaultTreatment)}&source=chatbot" class="small text-decoration-none text-primary fw-bold" style="font-size:0.75rem;">
            Open Full Interactive Booking Funnel →
          </a>
        </div>
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

  // Callout speech bubble management
  const callout = document.getElementById('cfChatCallout');
  const calloutClose = document.getElementById('cfCalloutClose');

  if (callout && !localStorage.getItem('carefirst_callout_dismissed')) {
    setTimeout(() => {
      if (!isOpen && callout) {
        callout.classList.add('show');
      }
    }, 2800);
  }

  if (calloutClose) {
    calloutClose.addEventListener('click', (e) => {
      e.stopPropagation();
      if (callout) callout.classList.remove('show');
      localStorage.setItem('carefirst_callout_dismissed', 'true');
    });
  }

  // ── Context-Aware Dynamic Launcher Engine ──
  let inactivityTimer = null;
  let isInactive = false;
  let currentBadgeState = '';

  function getPageContextMessage() {
    const path = window.location.pathname.toLowerCase();

    // Treatment Pages (e.g. /en/services/root-canal/, /services/, /treatments/)
    if (path.includes('/services') || path.includes('/treatments')) {
      const parts = path.split('/').filter(Boolean);
      // If viewing a specific treatment detail
      if (parts.length >= 2 && !['services', 'treatments', 'en', 'ne'].includes(parts[parts.length - 1])) {
        return { emoji: '🦷', title: 'Questions about this treatment?', sub: 'CareFirst AI • Online' };
      }
      return { emoji: '🦷', title: 'Questions about treatments?', sub: 'CareFirst AI • Online' };
    }

    // Pricing Page (e.g. /pricing/, /en/pricing/)
    if (path.includes('/pricing')) {
      return { emoji: '💰', title: 'Need help with pricing?', sub: 'CareFirst AI • Online' };
    }

    // Appointment / Booking Page (e.g. /appointment/, /en/appointment/, /contact/#book)
    if (path.includes('/appointment') || path.includes('/book')) {
      return { emoji: '📅', title: 'Need help booking?', sub: 'CareFirst AI • Online' };
    }

    // Default / Homepage / Other Pages
    return { emoji: '👋', title: 'Need dental help?', sub: 'CareFirst AI • Online' };
  }

  function getInactivityMessage() {
    return { emoji: '💬', title: 'Have a question?', sub: 'CareFirst AI • Online' };
  }

  function updateLauncherBadge(emoji, title, sub, force = false) {
    const key = `${emoji}-${title}`;
    if (!force && currentBadgeState === key) return;
    currentBadgeState = key;

    const emojiEl = document.getElementById('cfLauncherEmoji');
    const textWrap = document.getElementById('cfLauncherTextWrapper');
    const titleEl = document.getElementById('cfLauncherTitle');
    const subEl = document.getElementById('cfLauncherSub');

    if (!textWrap || !titleEl) return;

    // Smooth subtle crossfade without jumping
    textWrap.classList.add('cf-text-fade-out');
    if (emojiEl) emojiEl.style.opacity = '0';

    setTimeout(() => {
      if (emojiEl) {
        emojiEl.textContent = emoji;
        emojiEl.style.opacity = '1';
      }
      if (titleEl) titleEl.textContent = title;
      if (subEl) subEl.textContent = sub;

      textWrap.classList.remove('cf-text-fade-out');
      textWrap.classList.add('cf-text-fade-in');

      setTimeout(() => {
        textWrap.classList.remove('cf-text-fade-in');
      }, 250);
    }, 200);
  }

  function resetInactivityTimer() {
    if (isOpen) return;

    if (isInactive) {
      isInactive = false;
      const ctx = getPageContextMessage();
      updateLauncherBadge(ctx.emoji, ctx.title, ctx.sub);
    }

    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
      if (!isOpen) {
        isInactive = true;
        const msg = getInactivityMessage();
        updateLauncherBadge(msg.emoji, msg.title, msg.sub);
      }
    }, 7000); // 7 seconds of inactivity
  }

  function initContextAwareBadge() {
    const ctx = getPageContextMessage();
    updateLauncherBadge(ctx.emoji, ctx.title, ctx.sub, true);

    ['mousemove', 'scroll', 'keydown', 'touchstart', 'click'].forEach(evt => {
      window.addEventListener(evt, resetInactivityTimer, { passive: true });
    });

    resetInactivityTimer();
  }

  // ── Automatic Chat Engine & History Restoration on DOM Ready ──
  function initChatEngine() {
    initContextAwareBadge();

    // 1. Immediately render local history so user never sees messages wiped out
    const localMsgs = getLocalHistory();
    if (localMsgs && localMsgs.length > 0) {
      if (body) {
        body.innerHTML = '';
        localMsgs.forEach(m => {
          appendMessage(m.role, m.content, m.created_at, m.cards, m.quick_actions, m.id, false);
        });
      }
    }

    // 2. Restore open state if it was open before refresh
    if (isOpen) {
      if (panel) panel.classList.add('active');
      if (launcher) launcher.classList.add('is-open');
      if (input) input.focus();
    }

    // 3. Background server history sync
    loadHistory(false);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatEngine);
  } else {
    initChatEngine();
  }


  // Event Listeners
  if (launcher) launcher.addEventListener('click', () => {
    if (callout) callout.classList.remove('show');
    toggleChat();
  });
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
