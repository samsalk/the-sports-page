/* Main Application Logic */

let currentData = null;
let currentPrefs = null;

// Main initialization
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Load user preferences from localStorage
        currentPrefs = loadPreferences();
        applyPreferences(currentPrefs);

        // Fetch sports data
        currentData = await fetchSportsData();

        // Update date/time display
        updateMetadata(currentData);

        // Render content
        renderAllLeagues(currentData, currentPrefs);

        // Attach event listeners
        attachEventListeners();

    } catch (error) {
        console.error('Failed to load sports data:', error);
        showError('Unable to load sports data. Please try again later.');
    }
});

async function fetchSportsData() {
    const response = await fetch('data/sports_data.json');
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
}

function updateMetadata(data) {
    // Update date label
    const dateLabel = document.getElementById('dateLabel');
    if (dateLabel && data.date_label) {
        dateLabel.textContent = data.date_label;
    }

    // Update generation time
    const updateTime = document.getElementById('updateTime');
    if (updateTime && data.generated_at) {
        updateTime.textContent = formatTime(data.generated_at);
    }

    // Update page title
    if (data.date_label) {
        document.title = `The Sports Page - ${data.date_label}`;
    }
}

function applyPreferences(prefs) {
    // Set league checkboxes
    for (const [league, enabled] of Object.entries(prefs.leagues)) {
        const checkbox = document.getElementById(`toggle-${league}`);
        if (checkbox) {
            checkbox.checked = enabled;
        }
    }

    // Set box score toggle
    const boxScoreToggle = document.getElementById('toggle-boxscores');
    if (boxScoreToggle) {
        boxScoreToggle.checked = prefs.showBoxScores;
    }
}

function attachEventListeners() {
    // League toggles
    document.querySelectorAll('.league-toggles input').forEach(checkbox => {
        checkbox.addEventListener('change', handleLeagueToggle);
    });

    // Box score toggle
    const boxScoreToggle = document.getElementById('toggle-boxscores');
    if (boxScoreToggle) {
        boxScoreToggle.addEventListener('change', handleBoxScoreToggle);
    }
}

function handleLeagueToggle(event) {
    const leagueKey = event.target.id.replace('toggle-', '');
    currentPrefs = updatePreference(`league-${leagueKey}`, event.target.checked);

    // Re-render
    if (currentData) {
        renderAllLeagues(currentData, currentPrefs);
    }
}

function handleBoxScoreToggle(event) {
    currentPrefs = updatePreference('showBoxScores', event.target.checked);

    // Re-render
    if (currentData) {
        renderAllLeagues(currentData, currentPrefs);
    }
}
