const API_URL = 'https://first-chatbot-backend.onrender.com';
let conversationHistory = [];

// Configure marked.js for markdown rendering
marked.setOptions({
    breaks: true,
    gfm: true,
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
    }
});

// Dark mode toggle
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Load dark mode preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}

// Check API health on load
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_URL}/api/health`);
        const data = await response.json();
        document.getElementById('provider').textContent = 
            data.provider === 'gemini' ? '🔷 Gemini' : '🤖 OpenAI';
    } catch (error) {
        console.error('Failed to check API health:', error);
    }
}

// Send message function
async function sendMessage(event) {
    event.preventDefault();
    
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Check if research mode is enabled
    const researchMode = document.getElementById('researchMode').checked;
    
    // Clear input
    input.value = '';
    
    // Hide welcome message
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.remove();
    
    // Add user message to UI
    addMessage(message, 'user');
    
    // Add typing indicator
    const typingId = addTypingIndicator();
    
    // Disable send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    
    try {
        if (researchMode) {
            // Research mode - use multi-agent workflow
            await handleResearchMode(message, typingId);
        } else {
            // Normal chat mode
            await handleNormalChat(message, typingId);
        }
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator(typingId);
        addMessage('Sorry, I encountered an error connecting to the server. Please try again.', 'assistant', true);
    } finally {
        sendBtn.disabled = false;
    }
}

// Handle normal chat mode
async function handleNormalChat(message, typingId) {
    const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            conversationHistory: conversationHistory.slice(-10)
        })
    });
    
    if (!response.ok) {
        throw new Error('Failed to get response from server');
    }
    
    const data = await response.json();
    
    // Remove typing indicator
    removeTypingIndicator(typingId);
    
    // Add assistant message
    addMessage(data.reply, 'assistant');
    
    // Update conversation history
    conversationHistory.push(
        { role: 'user', content: message },
        { role: 'assistant', content: data.reply }
    );
}

// Handle research mode - multi-agent workflow
async function handleResearchMode(topic, typingId) {
    // Update typing indicator to show research status
    updateTypingIndicator(typingId, '🔬 Researching...');
    
    const response = await fetch(`${API_URL}/api/research`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic })
    });
    
    if (!response.ok) {
        throw new Error('Failed to generate research report');
    }
    
    const data = await response.json();
    
    // Remove typing indicator
    removeTypingIndicator(typingId);
    
    // Add research report with special formatting
    addResearchReport(data.report);
    
    // Update conversation history
    conversationHistory.push(
        { role: 'user', content: topic },
        { role: 'assistant', content: data.report }
    );
}

// Add research report with special formatting
function addResearchReport(report) {
    const messagesContainer = document.getElementById('messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant research-report';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const roleSpan = document.createElement('div');
    roleSpan.className = 'message-role';
    roleSpan.innerHTML = '🔬 Research Report';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    // Convert line breaks to HTML
    textDiv.innerHTML = report.replace(/\n/g, '<br>');
    
    contentDiv.appendChild(roleSpan);
    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Update typing indicator text
function updateTypingIndicator(id, text) {
    const element = document.getElementById(id);
    if (element) {
        const contentDiv = element.querySelector('.message-content');
        if (contentDiv) {
            contentDiv.innerHTML = `<div class="research-status">${text}</div>`;
        }
    }
}

// Add message to UI with markdown rendering
function addMessage(text, role, isError = false) {
    const messagesContainer = document.getElementById('messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}${isError ? ' error' : ''}`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.textContent = role === 'user' ? 'You' : 'JS';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    
    const roleSpan = document.createElement('span');
    roleSpan.className = 'message-role';
    roleSpan.textContent = role === 'user' ? 'You' : 'J Sai Deepak Style AI';
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    
    headerDiv.appendChild(roleSpan);
    headerDiv.appendChild(timeSpan);
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    if (role === 'assistant' && !isError) {
        // Render markdown for assistant messages
        textDiv.innerHTML = marked.parse(text);
        // Highlight code blocks
        textDiv.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    } else {
        textDiv.textContent = text;
    }
    
    contentDiv.appendChild(headerDiv);
    contentDiv.appendChild(textDiv);
    
    // Add copy button for assistant messages
    if (role === 'assistant' && !isError) {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>`;
        copyBtn.title = 'Copy message';
        copyBtn.onclick = () => copyMessage(text, copyBtn);
        contentDiv.appendChild(copyBtn);
    }
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Add research report with special formatting
function addResearchReport(report) {
    const messagesContainer = document.getElementById('messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant research-report';
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar research';
    avatarDiv.textContent = '🔬';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    
    const roleSpan = document.createElement('span');
    roleSpan.className = 'message-role';
    roleSpan.innerHTML = '🔬 Multi-Agent Research Report';
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    
    headerDiv.appendChild(roleSpan);
    headerDiv.appendChild(timeSpan);
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    // Render markdown
    textDiv.innerHTML = marked.parse(report);
    textDiv.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
    
    contentDiv.appendChild(headerDiv);
    contentDiv.appendChild(textDiv);
    
    // Add copy button
    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
    </svg>`;
    copyBtn.title = 'Copy report';
    copyBtn.onclick = () => copyMessage(report, copyBtn);
    contentDiv.appendChild(copyBtn);
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Copy message to clipboard
function copyMessage(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        const originalHTML = button.innerHTML;
        button.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="20 6 9 17 4 12"></polyline>
        </svg>`;
        setTimeout(() => {
            button.innerHTML = originalHTML;
        }, 2000);
    });
}

// Update typing indicator text
function updateTypingIndicator(id, text) {
    const element = document.getElementById(id);
    if (element) {
        const contentDiv = element.querySelector('.message-content');
        if (contentDiv) {
            contentDiv.innerHTML = `<div class="research-status">${text}</div>`;
        }
    }
}

// Add typing indicator
function addTypingIndicator() {
    const messagesContainer = document.getElementById('messages');
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant';
    typingDiv.id = 'typing-indicator';
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.textContent = 'JS';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content typing-content';
    
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    
    contentDiv.appendChild(indicator);
    typingDiv.appendChild(avatarDiv);
    typingDiv.appendChild(contentDiv);
    messagesContainer.appendChild(typingDiv);
    
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return 'typing-indicator';
}

// Remove typing indicator
function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) element.remove();
}

// Clear chat function
function clearChat() {
    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-avatar">JS</div>
            <h2>👋 Namaste!</h2>
            <p>I'm here to engage in thoughtful, analytical discussions. Ask me anything about law, history, culture, philosophy, or current affairs.</p>
            <p class="mode-hint">💡 Enable <strong>Research Mode</strong> for comprehensive multi-agent analysis</p>
        </div>
    `;
    conversationHistory = [];
}

// Initialize on page load
window.addEventListener('load', () => {
    checkAPIHealth();
    document.getElementById('messageInput').focus();
});
