/* LocalStorage Management */

const DEFAULT_PREFERENCES = {
    leagues: {
        nhl: true,
        nba: true,
        epl: true,
        mlb: true,
        nfl: false
    },
    showBoxScores: false
};

function loadPreferences() {
    const stored = localStorage.getItem('sportsPagePrefs');
    if (stored) {
        try {
            return { ...DEFAULT_PREFERENCES, ...JSON.parse(stored) };
        } catch (e) {
            console.error('Failed to parse preferences:', e);
        }
    }
    return DEFAULT_PREFERENCES;
}

function savePreferences(prefs) {
    localStorage.setItem('sportsPagePrefs', JSON.stringify(prefs));
}

function updatePreference(key, value) {
    const prefs = loadPreferences();
    if (key.startsWith('league-')) {
        const league = key.replace('league-', '');
        prefs.leagues[league] = value;
    } else {
        prefs[key] = value;
    }
    savePreferences(prefs);
    return prefs;
}
