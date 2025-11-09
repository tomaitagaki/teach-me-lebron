// Global state
let userPreferences = null;
let currentEventSource = null;
let isStreaming = false;

// Initialize onboarding
async function initOnboarding() {
    const location = document.getElementById('locationSelect').value;

    try {
        const response = await fetch(`/api/onboarding/default-teams/${location}`);
        const preferences = await response.json();

        userPreferences = preferences;
        displayTeams(preferences.teams);
    } catch (error) {
        console.error('Error loading teams:', error);
        showError('Failed to load team preferences. Please try again.');
    }
}

function displayTeams(teams) {
    const teamsList = document.getElementById('teamsList');
    teamsList.innerHTML = '<h3>Your Teams:</h3>';

    teams.forEach(team => {
        const teamItem = document.createElement('div');
        teamItem.className = 'team-item';
        teamItem.innerHTML = `
            <strong>${team.team_name}</strong>
            <span style="margin-left: auto; color: #65676b; font-size: 13px;">
                ${team.sport.toUpperCase()}
                ${team.is_local ? ' • Local' : ''}
            </span>
        `;
        teamsList.appendChild(teamItem);
    });
}

async function completeOnboarding() {
    document.getElementById('onboarding').classList.remove('active');
    document.getElementById('chatContainer').classList.add('active');

    // Show clear history button
    document.getElementById('clearHistoryBtn').style.display = 'block';

    // Load chat history first
    await loadChatHistory();

    // Check for proactive news on startup
    checkForProactiveNews();
}

async function loadChatHistory() {
    const userId = 'default_user';

    try {
        const response = await fetch(`/api/chat/history/${userId}?limit=20`);
        if (!response.ok) {
            console.error('Failed to load chat history');
            return;
        }

        const data = await response.json();
        const messages = data.messages || [];

        // Clear initial welcome message
        const messagesDiv = document.getElementById('messages');
        messagesDiv.innerHTML = '';

        // Display messages from history
        for (const msg of messages) {
            if (msg.role === 'user') {
                addUserMessage(msg.content);
            } else if (msg.role === 'assistant') {
                addAssistantMessage(msg.content);

                // Add clips if present
                if (msg.clips && msg.clips.length > 0) {
                    for (const clip of msg.clips) {
                        addVideoClip(clip);
                    }
                }
            }
        }

        // If no history, show welcome message
        if (messages.length === 0) {
            addAssistantMessage('Ask me about sports history, current events, or request the latest news on your teams.');
        }

        console.log(`Loaded ${messages.length} messages from history`);
    } catch (error) {
        console.error('Error loading chat history:', error);
        // Show welcome message on error
        addAssistantMessage('Ask me about sports history, current events, or request the latest news on your teams.');
    }
}

async function checkForProactiveNews() {
    if (!userPreferences) return;

    try {
        const response = await fetch('/api/chat/check-news', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userPreferences)
        });

        const result = await response.json();

        if (result.should_notify && result.news_count > 0) {
            // Automatically show news
            setTimeout(() => {
                addAssistantMessage('I noticed there\'s some important sports news! Let me fill you in...');
                setTimeout(() => {
                    sendMessage('What\'s the latest news?', false);
                }, 500);
            }, 1000);
        }
    } catch (error) {
        console.error('Error checking for news:', error);
    }
}

function addUserMessage(text) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `<div class="message-content">${escapeHtml(text)}</div>`;
    messagesDiv.appendChild(messageDiv);
    scrollToBottom();
}

function addAssistantMessage(text) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.innerHTML = `<div class="message-content">${formatMessage(text)}</div>`;
    messagesDiv.appendChild(messageDiv);
    scrollToBottom();
    return messageDiv;
}

function addTypingIndicator() {
    const messagesDiv = document.getElementById('messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    messagesDiv.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function formatMessage(text) {
    // Convert markdown-style formatting to HTML
    let formatted = escapeHtml(text);

    // Bold
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function addVideoClip(clip) {
    const messagesDiv = document.getElementById('messages');
    const clipDiv = document.createElement('div');
    clipDiv.className = 'message assistant';

    const youtubeUrl = `https://www.youtube.com/embed/${clip.youtube_id}`;
    const timestampParam = clip.timestamp ? `?start=${clip.timestamp}` : '';

    clipDiv.innerHTML = `
        <div class="message-content">
            <div class="video-embed">
                <iframe
                    src="${youtubeUrl}${timestampParam}"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen
                ></iframe>
                <div class="video-caption">
                    <strong>${escapeHtml(clip.title)}</strong><br>
                    ${escapeHtml(clip.description)}
                </div>
            </div>
        </div>
    `;

    messagesDiv.appendChild(clipDiv);
    scrollToBottom();
}

async function sendMessage(messageText = null, showUserMessage = true) {
    const input = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');

    const message = messageText || input.value.trim();

    if (!message || isStreaming) return;

    if (showUserMessage) {
        addUserMessage(message);
    }

    input.value = '';
    input.disabled = true;
    sendBtn.disabled = true;
    isStreaming = true;

    addTypingIndicator();

    try {
        // Create the request payload
        const payload = {
            message: message,
            user_id: 'default_user',
            preferences: userPreferences
        };

        const response = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        removeTypingIndicator();

        // Handle SSE stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessage = '';
        let messageDiv = null;

        while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);

                    if (data === '[DONE]') continue;

                    try {
                        const parsed = JSON.parse(data);

                        if (parsed.type === 'start') {
                            // Create initial message div
                            messageDiv = addAssistantMessage('');
                        } else if (parsed.type === 'token' && parsed.content) {
                            // Append token to message
                            assistantMessage += parsed.content;
                            if (messageDiv) {
                                const contentDiv = messageDiv.querySelector('.message-content');
                                contentDiv.innerHTML = formatMessage(assistantMessage);
                                scrollToBottom();
                            }
                        } else if (parsed.type === 'clip' && parsed.clip) {
                            // Add video clip
                            addVideoClip(parsed.clip);
                        } else if (parsed.type === 'done') {
                            // Stream complete
                            break;
                        } else if (parsed.type === 'error') {
                            showError(parsed.content);
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                }
            }
        }

    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator();
        showError('Sorry, I encountered an error. Please try again.');
    } finally {
        input.disabled = false;
        sendBtn.disabled = false;
        isStreaming = false;
        input.focus();
    }
}

function sendSuggestion(element) {
    const suggestion = element.textContent;
    sendMessage(suggestion);
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function scrollToBottom() {
    const messagesDiv = document.getElementById('messages');
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showError(message) {
    const messagesDiv = document.getElementById('messages');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';

    // Parse error message for special cases
    if (message.includes('Rate limit')) {
        errorDiv.innerHTML = `
            <strong>Rate Limit Reached</strong><br>
            The free API tier has limited requests. Please wait a moment before trying again.
        `;
    } else if (message.includes('authentication') || message.includes('API key')) {
        errorDiv.innerHTML = `
            <strong>API Configuration Error</strong><br>
            Please check your OpenRouter API key in the .env file.
        `;
    } else if (message.includes('Network')) {
        errorDiv.innerHTML = `
            <strong>Connection Error</strong><br>
            Please check your internet connection and try again.
        `;
    } else {
        errorDiv.textContent = message;
    }

    messagesDiv.appendChild(errorDiv);
    scrollToBottom();

    // Remove error after 10 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 10000);
}

async function clearHistory() {
    const userId = 'default_user';

    if (!confirm('Are you sure you want to clear your chat history? This cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/api/chat/history/${userId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            // Clear UI
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML = '';
            addAssistantMessage('Chat history cleared. Ask me anything about sports!');
        } else {
            showError('Failed to clear chat history. Please try again.');
        }
    } catch (error) {
        console.error('Error clearing history:', error);
        showError('Failed to clear chat history. Please try again.');
    }
}

// Initialize on page load
window.addEventListener('load', () => {
    initOnboarding();

    // Handle location change
    document.getElementById('locationSelect').addEventListener('change', initOnboarding);
});
