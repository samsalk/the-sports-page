/* Helper Utility Functions */

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

function createElement(tag, className, content) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (content) el.textContent = content;
    return el;
}

function showError(message) {
    const content = document.getElementById('content');
    content.innerHTML = `<div class="error">${message}</div>`;
}

function getLeagueName(key) {
    const names = {
        nhl: 'NHL',
        epl: 'Premier League',
        nba: 'NBA',
        mlb: 'MLB',
        nfl: 'NFL'
    };
    return names[key] || key.toUpperCase();
}
