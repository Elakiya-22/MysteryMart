/**
 * MysteryMart — Floating AI Customer Support Assistant Widget
 * Reusable across every page including custom error pages.
 */

let chatSessionId = localStorage.getItem('mm_chat_session_id') || ('chat_' + Math.random().toString(36).substring(2, 12));
localStorage.setItem('mm_chat_session_id', chatSessionId);

document.addEventListener('DOMContentLoaded', () => {
  const launcher = document.getElementById('mmChatLauncher');
  const chatWindow = document.getElementById('mmChatWindow');
  const closeBtn = document.getElementById('mmChatClose');
  const sendBtn = document.getElementById('mmChatSend');
  const chatInput = document.getElementById('mmChatInput');
  const messagesBox = document.getElementById('mmChatMessages');

  if (!launcher || !chatWindow) return;

  // Toggle Chat Window
  launcher.addEventListener('click', () => {
    chatWindow.classList.toggle('open');
    if (chatWindow.classList.contains('open')) {
      if (chatInput) chatInput.focus();
      scrollChatToBottom();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      chatWindow.classList.remove('open');
    });
  }

  // Send message on Enter or Click
  if (sendBtn && chatInput) {
    sendBtn.addEventListener('click', () => sendMessage());
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  // Pre-seed Welcome Message if empty
  if (messagesBox && messagesBox.children.length === 0) {
    appendBotMessage({
      response: "👋 **Welcome to MysteryMart!** I'm your Unboxing Concierge. Ask me about our mystery box categories, delivery timelines, guaranteed inclusions, or HTTP error codes!",
      source: 'system',
      actions: ['What is inside a Gadget Box?', 'Delivery timelines & fees', 'What is error 460?', 'Open Support Ticket']
    });
  }

  // Global trigger function to open chat and ask an automated query (e.g. from 404 or 500 error pages!)
  window.askAssistant = function(prefillMessage) {
    chatWindow.classList.add('open');
    if (prefillMessage) {
      if (chatInput) chatInput.value = prefillMessage;
      sendMessage();
    }
  };
});

/**
 * Send user message to Assistant API
 */
async function sendMessage(textOverride) {
  const chatInput = document.getElementById('mmChatInput');
  const message = textOverride || (chatInput ? chatInput.value.trim() : '');
  if (!message) return;

  if (chatInput && !textOverride) {
    chatInput.value = '';
  }

  // Append User Bubble
  appendUserMessage(message);
  scrollChatToBottom();

  // Show typing indicator
  const typingId = showTypingIndicator();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: message,
        session_id: chatSessionId
      })
    });

    removeTypingIndicator(typingId);

    if (res.status === 429) {
      appendBotMessage({
        response: "⏳ **Rate Limit Alert (HTTP 429):** You're sending messages very quickly! Please pause for a moment before retrying.",
        source: 'system'
      });
      return;
    }

    const data = await res.json();
    appendBotMessage(data);

  } catch (err) {
    console.error('Chat error:', err);
    removeTypingIndicator(typingId);
    appendBotMessage({
      response: "I encountered a brief connection issue. Would you like to view our [FAQs](/faq) or [Open a Support Ticket](/support)?",
      offer_ticket: true
    });
  } finally {
    scrollChatToBottom();
  }
}

function appendUserMessage(text) {
  const box = document.getElementById('mmChatMessages');
  if (!box) return;

  const row = document.createElement('div');
  row.className = 'chat-message-row user animate__animated animate__fadeInUp';
  row.innerHTML = `
    <div class="chat-bubble">${escapeHtml(text)}</div>
    <div class="chat-msg-meta text-end">Just now</div>
  `;
  box.appendChild(row);
}

function appendBotMessage(data) {
  const box = document.getElementById('mmChatMessages');
  if (!box) return;

  const row = document.createElement('div');
  row.className = 'chat-message-row assistant animate__animated animate__fadeIn';

  // Format markdown-like bold and links
  let formattedText = formatSimpleMarkdown(data.response || '');

  let badgeHtml = '';
  if (data.source === 'verified_faq') {
    badgeHtml = `<div class="verified-faq-badge"><i class="bi bi-shield-check"></i> Verified SQL Knowledge Base</div>`;
  } else if (data.source === 'http_knowledge_base') {
    badgeHtml = `<div class="verified-faq-badge" style="background:#FEF3C7;color:#92400E;"><i class="bi bi-info-circle"></i> HTTP Diagnostics</div>`;
  }

  // Suggestion action chips
  let actionsHtml = '';
  const actionsList = data.actions || data.suggested_questions || [];
  if (actionsList.length > 0) {
    actionsHtml = `<div class="chat-suggestions-container">`;
    actionsList.forEach(act => {
      actionsHtml += `<button class="suggestion-chip" onclick="handleSuggestionClick('${escapeHtml(act)}')">${escapeHtml(act)}</button>`;
    });
    actionsHtml += `</div>`;
  }

  // Ticket creation card
  let ticketCardHtml = '';
  if (data.offer_ticket) {
    ticketCardHtml = `
      <div class="chat-ticket-card">
        <div class="fw-bold text-dark small"><i class="bi bi-ticket-perforated"></i> Need Concierge Escalation?</div>
        <p class="text-muted small mb-2">Our support team can research your inquiry directly.</p>
        <button class="chat-ticket-btn" onclick="openInlineTicketModal()">
          <i class="bi bi-plus-circle"></i> Open Support Ticket
        </button>
      </div>
    `;
  }

  row.innerHTML = `
    <div class="chat-bubble">
      ${badgeHtml}
      <div>${formattedText}</div>
      ${ticketCardHtml}
      ${actionsHtml}
    </div>
    <div class="chat-msg-meta">${data.mode || 'MysteryMart Concierge'}</div>
  `;

  box.appendChild(row);
}

function handleSuggestionClick(text) {
  if (text === 'Open Support Ticket') {
    openInlineTicketModal();
  } else {
    sendMessage(text);
  }
}

function showTypingIndicator() {
  const box = document.getElementById('mmChatMessages');
  if (!box) return null;
  const id = 'typing_' + Date.now();
  const row = document.createElement('div');
  row.id = id;
  row.className = 'chat-message-row assistant';
  row.innerHTML = `
    <div class="chat-bubble py-2 px-3 text-muted">
      <span class="spinner-grow spinner-grow-sm me-1" style="width: 8px; height: 8px; background-color:#7C3AED;"></span>
      <span class="spinner-grow spinner-grow-sm me-1" style="width: 8px; height: 8px; background-color:#EA580C;"></span>
      <span class="spinner-grow spinner-grow-sm" style="width: 8px; height: 8px; background-color:#8B5CF6;"></span>
    </div>
  `;
  box.appendChild(row);
  scrollChatToBottom();
  return id;
}

function removeTypingIndicator(id) {
  if (!id) return;
  const el = document.getElementById(id);
  if (el) el.remove();
}

function scrollChatToBottom() {
  const box = document.getElementById('mmChatMessages');
  if (box) {
    box.scrollTop = box.scrollHeight;
  }
}

function formatSimpleMarkdown(text) {
  return text
    .replace(/^### (.*$)/gim, '<h6 class="fw-bold mb-1 mt-2">$1</h6>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code class="bg-light px-1 rounded text-purple">$1</code>')
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" class="fw-bold text-decoration-underline">$1</a>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Inline support ticket modal generator inside chat
 */
function openInlineTicketModal() {
  const box = document.getElementById('mmChatMessages');
  if (!box) return;

  const formId = 'inline_tkt_' + Date.now();
  const row = document.createElement('div');
  row.className = 'chat-message-row assistant';
  row.innerHTML = `
    <div class="chat-bubble p-3" style="border: 2px solid #EA580C;">
      <h6 class="fw-bold text-dark mb-2"><i class="bi bi-headset text-orange"></i> Quick Support Ticket Form</h6>
      <div id="${formId}">
        <div class="mb-2">
          <input type="text" id="${formId}_name" class="form-control form-control-sm" placeholder="Your Full Name">
        </div>
        <div class="mb-2">
          <input type="email" id="${formId}_email" class="form-control form-control-sm" placeholder="Your Email Address">
        </div>
        <div class="mb-2">
          <input type="text" id="${formId}_subject" class="form-control form-control-sm" placeholder="Short Subject">
        </div>
        <div class="mb-2">
          <textarea id="${formId}_desc" class="form-control form-control-sm" rows="2" placeholder="Describe what you need assistance with..."></textarea>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-mm-orange flex-grow-1" onclick="submitInlineTicket('${formId}')">Submit Ticket</button>
        </div>
      </div>
    </div>
  `;
  box.appendChild(row);
  scrollChatToBottom();
}

async function submitInlineTicket(formId) {
  const name = document.getElementById(`${formId}_name`)?.value.trim();
  const email = document.getElementById(`${formId}_email`)?.value.trim();
  const subject = document.getElementById(`${formId}_subject`)?.value.trim();
  const desc = document.getElementById(`${formId}_desc`)?.value.trim();

  if (!name || !email || !subject || !desc) {
    alert('Please fill in all ticket fields.');
    return;
  }

  const container = document.getElementById(formId);
  if (container) {
    container.innerHTML = '<div class="text-center py-2"><span class="spinner-border spinner-border-sm me-2"></span> Generating ticket in database...</div>';
  }

  try {
    const res = await fetch('/api/chat/ticket', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customer_name: name,
        customer_email: email,
        subject: subject,
        description: desc,
        session_id: chatSessionId
      })
    });

    const data = await res.json();
    if (res.ok && data.success) {
      if (container) {
        container.innerHTML = `
          <div class="alert alert-success py-2 px-3 small mb-0">
            <strong>✅ Success!</strong> Ticket Reference: <span class="badge bg-dark">${data.ticket_number}</span>
            <div class="mt-1">Saved to SQL database. You can track this on our <a href="/support" class="fw-bold">Support Page</a>.</div>
          </div>
        `;
      }
      // Offer feedback rating
      promptFeedbackForm();
    } else {
      if (container) {
        container.innerHTML = `<div class="alert alert-danger py-2 small mb-0">${data.message || 'Error creating ticket.'}</div>`;
      }
    }
  } catch (err) {
    if (container) {
      container.innerHTML = `<div class="alert alert-danger py-2 small mb-0">Failed to connect to ticket service.</div>`;
    }
  }
}

/**
 * Customer Feedback and Star Rating form
 */
function promptFeedbackForm() {
  const box = document.getElementById('mmChatMessages');
  if (!box) return;

  const fbRow = document.createElement('div');
  fbRow.className = 'chat-message-row assistant mt-2';
  fbRow.innerHTML = `
    <div class="chat-feedback-box">
      <div class="small fw-bold text-dark">Rate your concierge experience:</div>
      <div class="star-rating-row" id="chatStarRating">
        <i class="bi bi-star-fill active" data-rating="1"></i>
        <i class="bi bi-star-fill active" data-rating="2"></i>
        <i class="bi bi-star-fill active" data-rating="3"></i>
        <i class="bi bi-star-fill active" data-rating="4"></i>
        <i class="bi bi-star-fill active" data-rating="5"></i>
      </div>
      <button class="btn btn-sm btn-outline-secondary py-0 px-2 mt-1" onclick="submitFeedback(5)">Send Feedback</button>
    </div>
  `;
  box.appendChild(fbRow);
  scrollChatToBottom();
}

async function submitFeedback(rating) {
  try {
    await fetch('/api/chat/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rating: rating,
        comment: 'Submitted via Chat Widget',
        session_id: chatSessionId
      })
    });
    const ratingBox = document.getElementById('chatStarRating')?.parentElement;
    if (ratingBox) {
      ratingBox.innerHTML = '<span class="text-success small fw-bold">⭐ Thank you for rating our concierge!</span>';
    }
  } catch (e) {}
}
