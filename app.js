const API_URL = 'https://first-chatbot-backend.onrender.com';
let conversationHistory = [];

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

// Add message to UI
function addMessage(text, role, isError = false) {
    const messagesContainer = document.getElementById('messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}${isError ? ' error' : ''}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const roleSpan = document.createElement('div');
    roleSpan.className = 'message-role';
    roleSpan.textContent = role === 'user' ? '👤 You' : '🤖 Assistant';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.textContent = text;
    
    contentDiv.appendChild(roleSpan);
    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Add typing indicator
function addTypingIndicator() {
    const messagesContainer = document.getElementById('messages');
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant';
    typingDiv.id = 'typing-indicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    
    contentDiv.appendChild(indicator);
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
            <h2>👋 Welcome!</h2>
            <p>Start a conversation by typing a message below.</p>
            <p class="mode-hint">💡 Enable <strong>Research Mode</strong> for comprehensive multi-agent reports</p>
        </div>
    `;
    conversationHistory = [];
}

// Initialize on page load
window.addEventListener('load', () => {
    checkAPIHealth();
    document.getElementById('messageInput').focus();
});
