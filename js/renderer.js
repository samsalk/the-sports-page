/* Data Rendering Functions */

// Check if box score has any meaningful data to display
function hasBoxScoreData(boxScore) {
    if (!boxScore) return false;

    // Check for line score with actual values (NHL/NBA use arrays, MLB uses {innings: [...], runs, hits, errors})
    const hasLineScore = boxScore.line_score && boxScore.line_score.away && (
        (Array.isArray(boxScore.line_score.away) && boxScore.line_score.away.length > 0 && boxScore.line_score.away.some(v => v > 0)) ||
        (boxScore.line_score.away.innings && boxScore.line_score.away.innings.length > 0)
    );

    // Check for scorers
    const hasScorers = boxScore.scorers && boxScore.scorers.length > 0;

    // Check for goalies (NHL)
    const hasGoalies = boxScore.goalies && boxScore.goalies.length > 0;

    // Check for shots (NHL)
    const hasShots = boxScore.shots && (boxScore.shots.away > 0 || boxScore.shots.home > 0);

    // Check for EPL goals (soccer)
    const hasEplGoals = (boxScore.home_goals && boxScore.home_goals.length > 0) ||
        (boxScore.away_goals && boxScore.away_goals.length > 0);

    // Check for MLB batting data
    const hasBatting = (boxScore.away_batting && boxScore.away_batting.length > 0) ||
        (boxScore.home_batting && boxScore.home_batting.length > 0);

    return hasLineScore || hasScorers || hasGoalies || hasShots || hasEplGoals || hasBatting;
}

function renderAllLeagues(data, prefs) {
    const content = document.getElementById('content');
    content.setAttribute('aria-busy', 'true');
    content.innerHTML = '';

    let hasContent = false;

    for (const [leagueKey, leagueData] of Object.entries(data.leagues)) {
        if (prefs.leagues[leagueKey]) {
            const section = renderLeagueSection(leagueKey, leagueData, prefs);
            if (section) {
                content.appendChild(section);
                hasContent = true;
            }
        }
    }

    if (!hasContent) {
        content.innerHTML = '<div class="no-games" role="status">No leagues selected. Please select a league above.</div>';
    }

    content.setAttribute('aria-busy', 'false');
}

function renderLeagueSection(leagueKey, data, prefs) {
    const headerId = `${leagueKey}-header`;

    if (data.error) {
        const section = createElement('section', 'league-section');
        section.setAttribute('aria-labelledby', headerId);
        section.innerHTML = `
            <h2 class="section-header" id="${headerId}">${getLeagueName(leagueKey)}</h2>
            <div class="error" role="alert">Failed to load data: ${data.error}</div>
        `;
        return section;
    }

    let sectionClass = `league-section league-${leagueKey}`;
    if (leagueKey === 'mlb' && prefs.showBoxScores) {
        sectionClass += ' mlb-boxscores-on';
    }
    const section = createElement('section', sectionClass);
    section.setAttribute('aria-labelledby', headerId);

    // Section header
    const header = createElement('h2', 'section-header', getLeagueName(leagueKey));
    header.id = headerId;
    section.appendChild(header);

    // Render subsections - Standings first, then scores
    if (data.standings && Object.keys(data.standings).length > 0) {
        section.appendChild(renderStandings(data.standings, leagueKey));
    }

    if (data.yesterday && data.yesterday.games && data.yesterday.games.length > 0) {
        section.appendChild(renderYesterdayScores(data.yesterday, prefs.showBoxScores, leagueKey));
    }

    if (data.leaders && hasLeaders(data.leaders)) {
        section.appendChild(renderLeaders(data.leaders, leagueKey));
    }

    if (data.schedule && data.schedule.length > 0) {
        section.appendChild(renderScheduleGrid(data.schedule));
    }

    return section;
}

function hasLeaders(leaders) {
    return Object.values(leaders).some(arr => arr && arr.length > 0);
}

function renderYesterdayScores(yesterday, showBoxScores, leagueKey) {
    const container = createElement('div', 'yesterday-scores');
    container.setAttribute('role', 'region');
    container.setAttribute('aria-label', "Recent game scores");

    // For EPL, show "Last Matchday" with the date since games aren't daily
    let titleText = `Yesterday's Scores`;
    if (leagueKey === 'epl' && yesterday.date) {
        const matchDate = new Date(yesterday.date + 'T12:00:00');
        const today = new Date();
        today.setHours(12, 0, 0, 0);
        const diffDays = Math.round((today - matchDate) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) {
            titleText = `Today's Results`;
        } else if (diffDays === 1) {
            titleText = `Yesterday's Results`;
        } else {
            const dateStr = matchDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
            titleText = `Last Matchday (${dateStr})`;
        }
    }

    const title = createElement('h3', 'subsection-header', titleText);
    container.appendChild(title);

    // Create games container for multi-column layout
    const gamesContainer = createElement('div', 'games-container');

    yesterday.games.forEach(game => {
        const gameDiv = renderGame(game, showBoxScores);
        gamesContainer.appendChild(gameDiv);
    });

    container.appendChild(gamesContainer);
    return container;
}

function renderGame(game, showBoxScores) {
    const article = document.createElement('article');
    article.className = 'game';
    article.setAttribute('aria-label', `${game.away_team.name} ${game.away_team.score} at ${game.home_team.name} ${game.home_team.score}`);

    // Create table for aligned scores
    const table = document.createElement('table');
    table.className = 'game-table';
    table.setAttribute('aria-label', 'Game score');

    const tbody = document.createElement('tbody');

    // Away team row
    const awayRow = document.createElement('tr');
    awayRow.innerHTML = `
        <td class="team-name">${game.away_team.name}</td>
        <td class="team-score">${game.away_team.score}</td>
    `;
    tbody.appendChild(awayRow);

    // Home team row
    const homeRow = document.createElement('tr');
    homeRow.innerHTML = `
        <td class="team-name">${game.home_team.name}</td>
        <td class="team-score">${game.home_team.score}</td>
    `;
    tbody.appendChild(homeRow);

    table.appendChild(tbody);
    article.appendChild(table);

    // Status line
    const statusLine = createElement('div', 'game-status', game.status);
    article.appendChild(statusLine);

    // Box score (if available and enabled)
    if (game.box_score && showBoxScores && hasBoxScoreData(game.box_score)) {
        const boxScore = renderBoxScore(game, game.box_score);
        article.appendChild(boxScore);
    }

    return article;
}

function renderBoxScore(game, boxScoreData) {
    const div = createElement('div', 'box-score visible');

    // EPL/Soccer goal scorers - different format from other sports
    if (boxScoreData.home_goals !== undefined || boxScoreData.away_goals !== undefined) {
        return renderSoccerBoxScore(game, boxScoreData);
    }

    // MLB box score - full batting/pitching tables, newspaper style
    if (boxScoreData.away_batting !== undefined) {
        return renderBaseballBoxScore(game, boxScoreData);
    }

    // Line score table - only show if we have actual period/quarter data
    const hasLineScore = boxScoreData.line_score &&
        boxScoreData.line_score.away &&
        boxScoreData.line_score.away.length > 0 &&
        boxScoreData.line_score.away.some(v => v > 0);

    if (hasLineScore) {
        const table = document.createElement('table');
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');

        headerRow.innerHTML = '<th>Team</th>';
        const periods = Math.max(boxScoreData.line_score.away.length, boxScoreData.line_score.home.length);
        for (let i = 1; i <= periods; i++) {
            headerRow.innerHTML += `<th>${i}</th>`;
        }
        headerRow.innerHTML += '<th>T</th>';
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');

        // Away team row
        const awayRow = document.createElement('tr');
        awayRow.innerHTML = `<td>${game.away_team.abbr}</td>`;
        boxScoreData.line_score.away.forEach(goals => {
            awayRow.innerHTML += `<td>${goals}</td>`;
        });
        awayRow.innerHTML += `<td><strong>${game.away_team.score}</strong></td>`;
        tbody.appendChild(awayRow);

        // Home team row
        const homeRow = document.createElement('tr');
        homeRow.innerHTML = `<td>${game.home_team.abbr}</td>`;
        boxScoreData.line_score.home.forEach(goals => {
            homeRow.innerHTML += `<td>${goals}</td>`;
        });
        homeRow.innerHTML += `<td><strong>${game.home_team.score}</strong></td>`;
        tbody.appendChild(homeRow);

        table.appendChild(tbody);
        div.appendChild(table);
    }

    // Shots - only show if both teams have non-zero shots
    if (boxScoreData.shots && (boxScoreData.shots.away > 0 || boxScoreData.shots.home > 0)) {
        const shotsP = createElement('p', '');
        shotsP.innerHTML = `<strong>Shots:</strong> ${game.away_team.abbr} ${boxScoreData.shots.away}, ${game.home_team.abbr} ${boxScoreData.shots.home}`;
        div.appendChild(shotsP);
    }

    // Top Scorers (all leagues) - organized by team in two columns
    if (boxScoreData.scorers && boxScoreData.scorers.length > 0) {
        const scorersDiv = createElement('div', 'scorers-section');
        const header = createElement('p', 'scorers-header');
        header.innerHTML = '<strong>Top Scorers:</strong>';
        scorersDiv.appendChild(header);

        const scorersGrid = createElement('div', 'scorers-grid');

        // Separate scorers by team
        const awayTeamScorers = boxScoreData.scorers.filter(s => s.team === game.away_team.abbr);
        const homeTeamScorers = boxScoreData.scorers.filter(s => s.team === game.home_team.abbr);

        // Away team column
        const awayCol = createElement('div', 'scorers-column');
        awayCol.innerHTML = `<div class="team-label">${game.away_team.abbr}</div>`;
        awayTeamScorers.forEach(s => {
            if (s.goals !== undefined) {
                // NHL format: goals and assists
                awayCol.innerHTML += `${s.name}: ${s.goals}G ${s.assists}A<br>`;
            } else if (s.points !== undefined) {
                // NBA format: PTS, REB, AST, shooting splits
                const fgStr = s.fgm !== undefined ? `, ${s.fgm}-${s.fga} FG` : '';
                const fg3Str = s.fg3m !== undefined && s.fg3a > 0 ? `, ${s.fg3m}-${s.fg3a} 3PT` : '';
                awayCol.innerHTML += `${s.name}: ${s.points}p ${s.rebounds}r ${s.assists}a${fgStr}${fg3Str}<br>`;
            }
        });
        scorersGrid.appendChild(awayCol);

        // Home team column
        const homeCol = createElement('div', 'scorers-column');
        homeCol.innerHTML = `<div class="team-label">${game.home_team.abbr}</div>`;
        homeTeamScorers.forEach(s => {
            if (s.goals !== undefined) {
                // NHL format: goals and assists
                homeCol.innerHTML += `${s.name}: ${s.goals}G ${s.assists}A<br>`;
            } else if (s.points !== undefined) {
                // NBA format: PTS, REB, AST, shooting splits
                const fgStr = s.fgm !== undefined ? `, ${s.fgm}-${s.fga} FG` : '';
                const fg3Str = s.fg3m !== undefined && s.fg3a > 0 ? `, ${s.fg3m}-${s.fg3a} 3PT` : '';
                homeCol.innerHTML += `${s.name}: ${s.points}p ${s.rebounds}r ${s.assists}a${fgStr}${fg3Str}<br>`;
            }
        });
        scorersGrid.appendChild(homeCol);

        scorersDiv.appendChild(scorersGrid);
        div.appendChild(scorersDiv);
    }

    // Goalies (NHL) - shown after scorers in two-column format
    if (boxScoreData.goalies && boxScoreData.goalies.length > 0) {
        const goaliesDiv = createElement('div', 'goalies-section');
        goaliesDiv.innerHTML = '<div class="scorers-title">Goalies</div>';

        const goaliesGrid = createElement('div', 'scorers-grid');

        // Separate goalies by team
        const awayGoalies = boxScoreData.goalies.filter(g => g.team === game.away_team.abbr);
        const homeGoalies = boxScoreData.goalies.filter(g => g.team === game.home_team.abbr);

        // Away team column
        const awayCol = createElement('div', 'scorers-column');
        awayCol.innerHTML = `<div class="team-label">${game.away_team.abbr}</div>`;
        awayGoalies.forEach(g => {
            const savePct = g.shots > 0 ? (g.save_pct * 100).toFixed(1) : '0.0';
            awayCol.innerHTML += `${g.name}: ${g.saves}/${g.shots} (${savePct}%)<br>`;
        });
        goaliesGrid.appendChild(awayCol);

        // Home team column
        const homeCol = createElement('div', 'scorers-column');
        homeCol.innerHTML = `<div class="team-label">${game.home_team.abbr}</div>`;
        homeGoalies.forEach(g => {
            const savePct = g.shots > 0 ? (g.save_pct * 100).toFixed(1) : '0.0';
            homeCol.innerHTML += `${g.name}: ${g.saves}/${g.shots} (${savePct}%)<br>`;
        });
        goaliesGrid.appendChild(homeCol);

        goaliesDiv.appendChild(goaliesGrid);
        div.appendChild(goaliesDiv);
    }

    return div;
}

function renderStandings(standings, leagueKey) {
    const container = createElement('div', 'standings');
    container.setAttribute('role', 'region');
    container.setAttribute('aria-label', `${getLeagueName(leagueKey)} Standings`);

    const title = createElement('h3', 'subsection-header', 'Standings');
    container.appendChild(title);

    // Create standings container for multi-column layout
    const standingsContainer = createElement('div', 'standings-container');

    if (leagueKey === 'nhl') {
        // Group divisions by conference
        const conferences = {
            'Eastern Conference': ['Atlantic', 'Metropolitan'],
            'Western Conference': ['Central', 'Pacific']
        };

        for (const [conferenceName, divisionNames] of Object.entries(conferences)) {
            // Create conference container
            const confContainer = createElement('div', 'standings-conference');

            const confTitle = createElement('h4', 'conference-title', conferenceName);
            confContainer.appendChild(confTitle);

            // Add divisions for this conference
            for (const divisionName of divisionNames) {
                // Find matching division in standings (may have "Division" suffix)
                const fullDivisionName = Object.keys(standings).find(key => key.includes(divisionName));
                if (!fullDivisionName) continue;

                const teams = standings[fullDivisionName];
                if (teams.length === 0) continue;

                const divContainer = createElement('div', 'standings-division');
                const divTitle = createElement('h4', '', fullDivisionName);
                divContainer.appendChild(divTitle);

                const table = document.createElement('table');
                table.className = 'standings-table';
                table.setAttribute('aria-label', `${fullDivisionName} standings`);

                // Header with spelled-out abbreviations
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                headerRow.innerHTML = `
                    <th class="rank" scope="col">#</th>
                    <th class="team" scope="col">Team</th>
                    <th class="numeric" scope="col"><abbr title="Games Played">GP</abbr></th>
                    <th class="numeric" scope="col">Wins</th>
                    <th class="numeric" scope="col">Losses</th>
                    <th class="numeric" scope="col"><abbr title="Overtime Losses">OT</abbr></th>
                    <th class="numeric" scope="col">Points</th>
                    <th class="numeric" scope="col"><abbr title="Games Behind">GB</abbr></th>
                    <th scope="col">Streak</th>
                `;
                thead.appendChild(headerRow);
                table.appendChild(thead);

                // Body
                const tbody = document.createElement('tbody');
                teams.forEach(team => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="rank">${team.rank}</td>
                        <td class="team">${team.team_name}</td>
                        <td class="numeric">${team.games_played}</td>
                        <td class="numeric">${team.wins}</td>
                        <td class="numeric">${team.losses}</td>
                        <td class="numeric">${team.ot_losses}</td>
                        <td class="numeric"><strong>${team.points}</strong></td>
                        <td class="numeric">${team.games_behind}</td>
                        <td>${team.streak}</td>
                    `;
                    tbody.appendChild(row);
                });

                table.appendChild(tbody);
                divContainer.appendChild(table);
                confContainer.appendChild(divContainer);
            }

            standingsContainer.appendChild(confContainer);
        }
    } else if (leagueKey === 'nba') {
        // NBA has Eastern and Western conferences (no divisions shown)
        const conferences = ['Eastern', 'Western'];

        for (const conferenceName of conferences) {
            const teams = standings[conferenceName] || [];
            if (teams.length === 0) continue;

            const confContainer = createElement('div', 'standings-conference');

            const confTitle = createElement('h4', 'conference-title', conferenceName + ' Conference');
            confContainer.appendChild(confTitle);

            const table = document.createElement('table');
            table.className = 'standings-table';
            table.setAttribute('aria-label', `${conferenceName} Conference standings`);

            // Header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            headerRow.innerHTML = `
                <th class="rank" scope="col">#</th>
                <th class="team" scope="col">Team</th>
                <th class="numeric" scope="col"><abbr title="Wins">W</abbr></th>
                <th class="numeric" scope="col"><abbr title="Losses">L</abbr></th>
                <th class="numeric" scope="col"><abbr title="Win Percentage">PCT</abbr></th>
                <th class="numeric" scope="col"><abbr title="Games Behind">GB</abbr></th>
                <th scope="col">Streak</th>
            `;
            thead.appendChild(headerRow);
            table.appendChild(thead);

            // Body
            const tbody = document.createElement('tbody');
            teams.forEach(team => {
                const row = document.createElement('tr');
                const gb = team.games_back === 0 ? '-' : team.games_back;
                row.innerHTML = `
                    <td class="rank">${team.rank}</td>
                    <td class="team">${team.team_name}</td>
                    <td class="numeric">${team.wins}</td>
                    <td class="numeric">${team.losses}</td>
                    <td class="numeric">${team.win_pct.toFixed(3).replace('0.', '.')}</td>
                    <td class="numeric">${gb}</td>
                    <td>${team.streak}</td>
                `;
                tbody.appendChild(row);
            });

            table.appendChild(tbody);
            confContainer.appendChild(table);
            standingsContainer.appendChild(confContainer);
        }
    } else if (leagueKey === 'mlb') {
        // MLB: Group divisions by league (AL/NL), like newspaper box score pages
        const leagues = {
            'American League': ['AL East', 'AL Central', 'AL West'],
            'National League': ['NL East', 'NL Central', 'NL West']
        };

        for (const [leagueName, divisionNames] of Object.entries(leagues)) {
            const confContainer = createElement('div', 'standings-conference');
            const confTitle = createElement('h4', 'conference-title', leagueName);
            confContainer.appendChild(confTitle);

            for (const divisionName of divisionNames) {
                const teams = standings[divisionName];
                if (!teams || teams.length === 0) continue;

                const divContainer = createElement('div', 'standings-division');
                const divTitle = createElement('h4', '', divisionName);
                divContainer.appendChild(divTitle);

                const table = document.createElement('table');
                table.className = 'standings-table';
                table.setAttribute('aria-label', `${divisionName} standings`);

                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                headerRow.innerHTML = `
                    <th class="team" scope="col">Team</th>
                    <th class="numeric" scope="col"><abbr title="Wins">W</abbr></th>
                    <th class="numeric" scope="col"><abbr title="Losses">L</abbr></th>
                    <th class="numeric" scope="col"><abbr title="Win Percentage">PCT</abbr></th>
                    <th class="numeric" scope="col"><abbr title="Games Behind">GB</abbr></th>
                    <th scope="col">Streak</th>
                `;
                thead.appendChild(headerRow);
                table.appendChild(thead);

                const tbody = document.createElement('tbody');
                teams.forEach(team => {
                    const row = document.createElement('tr');
                    const gb = team.gb === '-' || team.gb === '0' || team.gb === 0 ? '-' : team.gb;
                    row.innerHTML = `
                        <td class="team">${team.team_name}</td>
                        <td class="numeric">${team.wins}</td>
                        <td class="numeric">${team.losses}</td>
                        <td class="numeric">${team.pct}</td>
                        <td class="numeric">${gb}</td>
                        <td>${team.streak || '-'}</td>
                    `;
                    tbody.appendChild(row);
                });

                table.appendChild(tbody);
                divContainer.appendChild(table);
                confContainer.appendChild(divContainer);
            }

            standingsContainer.appendChild(confContainer);
        }
    } else if (leagueKey === 'epl') {
        // EPL has single league table - use full width with spelled-out headers
        const divContainer = createElement('div', 'standings-division standings-full-width');

        const table = document.createElement('table');
        table.className = 'standings-table standings-table-wide';
        table.setAttribute('aria-label', 'Premier League standings');

        // Header with full column names (we have room)
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headerRow.innerHTML = `
            <th class="rank" scope="col">#</th>
            <th class="team" scope="col">Team</th>
            <th class="numeric" scope="col">Matches Played</th>
            <th class="numeric" scope="col">W</th>
            <th class="numeric" scope="col">D</th>
            <th class="numeric" scope="col">L</th>
            <th class="numeric" scope="col">Goals For</th>
            <th class="numeric" scope="col">Goals Against</th>
            <th class="numeric" scope="col">Goal Difference</th>
            <th class="numeric" scope="col">Points</th>
        `;
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Body - EPL standings are in a single "Premier League" key
        const teams = standings['Premier League'] || [];
        const tbody = document.createElement('tbody');
        teams.forEach(team => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="rank">${team.rank}</td>
                <td class="team team-nowrap">${team.team_name || team.team}</td>
                <td class="numeric">${team.played}</td>
                <td class="numeric">${team.wins}</td>
                <td class="numeric">${team.draws}</td>
                <td class="numeric">${team.losses}</td>
                <td class="numeric">${team.goals_for}</td>
                <td class="numeric">${team.goals_against}</td>
                <td class="numeric">${team.goal_diff > 0 ? '+' : ''}${team.goal_diff}</td>
                <td class="numeric"><strong>${team.points}</strong></td>
            `;
            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        divContainer.appendChild(table);
        standingsContainer.appendChild(divContainer);
    }

    container.appendChild(standingsContainer);
    return container;
}

function renderLeaders(leaders, leagueKey) {
    const container = createElement('div', 'leaders');
    container.setAttribute('role', 'region');
    container.setAttribute('aria-label', 'Statistical leaders');

    const title = createElement('h3', 'subsection-header', 'Statistical Leaders');
    container.appendChild(title);

    // Create leaders container for multi-column layout
    const leadersContainer = createElement('div', 'leaders-container');

    // Category display names per league
    const categoryLabels = leagueKey === 'nba' ? {
        'points': 'Points Per Game',
        'assists': 'Assists Per Game',
        'rebounds': 'Rebounds Per Game'
    } : leagueKey === 'mlb' ? {
        'batting_avg': 'Batting Average',
        'home_runs': 'Home Runs',
        'rbi': 'RBI',
        'hits': 'Hits',
        'stolen_bases': 'Stolen Bases',
        'wins': 'Wins',
        'era': 'ERA',
        'strikeouts': 'Strikeouts',
        'saves': 'Saves'
    } : {
        'goals': 'Goals',
        'assists': 'Assists',
        'points': 'Points',
        'saves': 'Saves'
    };

    for (const [category, playerList] of Object.entries(leaders)) {
        if (!playerList || playerList.length === 0) continue;

        const catDiv = createElement('div', 'leader-category');

        const label = categoryLabels[category] || category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ');
        const catTitle = createElement('h4', '', label);
        catDiv.appendChild(catTitle);

        const list = document.createElement('ul');
        list.className = 'leader-list';

        playerList.slice(0, 10).forEach(player => {
            const li = document.createElement('li');
            // Format value - show 1 decimal for per-game stats
            const isPerGame = ['points', 'assists', 'rebounds'].includes(category);
            const formattedValue = isPerGame ? Number(player.value).toFixed(1) : player.value;
            li.innerHTML = `
                <span class="rank">${player.rank}.</span>
                <span class="player">${player.player} <span class="team">(${player.team})</span></span>
                <span class="value">${formattedValue}</span>
            `;
            list.appendChild(li);
        });

        catDiv.appendChild(list);
        leadersContainer.appendChild(catDiv);
    }

    container.appendChild(leadersContainer);
    return container;
}

function renderScheduleGrid(schedule) {
    const container = createElement('div', 'schedule-grid');
    container.setAttribute('role', 'region');
    container.setAttribute('aria-label', "This week's schedule");

    const title = createElement('h3', 'subsection-header', 'This Week\'s Schedule');
    container.appendChild(title);

    if (schedule.length === 0) {
        container.appendChild(createElement('p', 'no-games', 'No games scheduled this week.'));
        return container;
    }

    const table = document.createElement('table');
    table.className = 'schedule-table';
    table.setAttribute('aria-label', 'Weekly game schedule');

    // Header row with days
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    schedule.forEach(day => {
        const th = document.createElement('th');
        th.setAttribute('scope', 'col');
        // Add time component to avoid timezone issues (date-only strings are parsed as UTC)
        const dateObj = new Date(day.date + 'T12:00:00');
        th.textContent = `${day.day_label} ${dateObj.getDate()}`;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Body with games
    const tbody = document.createElement('tbody');
    const bodyRow = document.createElement('tr');

    schedule.forEach(day => {
        const td = document.createElement('td');

        if (day.games.length === 0) {
            td.innerHTML = '<span class="no-games">No games</span>';
        } else {
            day.games.forEach(game => {
                const gameDiv = createElement('div', 'schedule-game');
                const awayRecord = game.away_record ? ` (${game.away_record})` : '';
                const homeRecord = game.home_record ? ` (${game.home_record})` : '';
                gameDiv.innerHTML = `
                    <span class="schedule-time">${game.time_label}</span>
                    <span class="schedule-matchup">${game.away_name || game.away}${awayRecord} @ ${game.home_name || game.home}${homeRecord}</span>
                `;
                td.appendChild(gameDiv);
            });
        }

        bodyRow.appendChild(td);
    });

    tbody.appendChild(bodyRow);
    table.appendChild(tbody);

    container.appendChild(table);
    return container;
}

function renderBaseballBoxScore(game, boxScoreData) {
    const div = createElement('div', 'box-score visible mlb-box-score');

    // Line score (inning-by-inning) with R/H/E
    const ls = boxScoreData.line_score;
    if (ls && ls.away && ls.away.innings) {
        const table = document.createElement('table');
        table.className = 'mlb-line-score';
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headerRow.innerHTML = '<th></th>';
        const numInnings = Math.max(ls.away.innings.length, ls.home.innings.length, 9);
        for (let i = 1; i <= numInnings; i++) {
            headerRow.innerHTML += `<th>${i}</th>`;
        }
        headerRow.innerHTML += '<th>R</th><th>H</th><th>E</th>';
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');

        // Away row
        const awayRow = document.createElement('tr');
        awayRow.innerHTML = `<td class="team-cell"><strong>${game.away_team.abbr}</strong></td>`;
        for (let i = 0; i < numInnings; i++) {
            const val = i < ls.away.innings.length ? ls.away.innings[i] : '';
            awayRow.innerHTML += `<td>${val}</td>`;
        }
        awayRow.innerHTML += `<td class="total"><strong>${ls.away.runs}</strong></td><td class="total">${ls.away.hits}</td><td class="total">${ls.away.errors}</td>`;
        tbody.appendChild(awayRow);

        // Home row
        const homeRow = document.createElement('tr');
        homeRow.innerHTML = `<td class="team-cell"><strong>${game.home_team.abbr}</strong></td>`;
        for (let i = 0; i < numInnings; i++) {
            const val = i < ls.home.innings.length ? ls.home.innings[i] : '';
            homeRow.innerHTML += `<td>${val}</td>`;
        }
        homeRow.innerHTML += `<td class="total"><strong>${ls.home.runs}</strong></td><td class="total">${ls.home.hits}</td><td class="total">${ls.home.errors}</td>`;
        tbody.appendChild(homeRow);

        table.appendChild(tbody);
        div.appendChild(table);
    }

    // Batting tables - one per team
    const renderBattingTable = (batters, teamAbbr) => {
        if (!batters || batters.length === 0) return null;

        const section = createElement('div', 'mlb-batting-section');
        const header = createElement('div', 'mlb-team-header', teamAbbr);
        section.appendChild(header);

        const table = document.createElement('table');
        table.className = 'mlb-batting-table';

        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headerRow.innerHTML = '<th class="player-col">Batter</th><th>AB</th><th>R</th><th>H</th><th>BI</th><th>BB</th><th>SO</th><th>AVG</th>';
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        let totals = { ab: 0, r: 0, h: 0, rbi: 0, bb: 0, so: 0 };

        batters.forEach(b => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="player-col">${b.name} <span class="pos">${b.position}</span></td>
                <td>${b.ab}</td><td>${b.r}</td><td>${b.h}</td><td>${b.rbi}</td><td>${b.bb}</td><td>${b.so}</td><td>${b.avg}</td>
            `;
            tbody.appendChild(row);
            totals.ab += b.ab;
            totals.r += b.r;
            totals.h += b.h;
            totals.rbi += b.rbi;
            totals.bb += b.bb;
            totals.so += b.so;
        });

        // Totals row
        const totalRow = document.createElement('tr');
        totalRow.className = 'totals-row';
        totalRow.innerHTML = `
            <td class="player-col"><strong>Totals</strong></td>
            <td><strong>${totals.ab}</strong></td><td><strong>${totals.r}</strong></td><td><strong>${totals.h}</strong></td><td><strong>${totals.rbi}</strong></td><td><strong>${totals.bb}</strong></td><td><strong>${totals.so}</strong></td><td></td>
        `;
        tbody.appendChild(totalRow);

        table.appendChild(tbody);
        section.appendChild(table);
        return section;
    };

    // Pitching tables - one per team
    const renderPitchingTable = (pitchers, teamAbbr) => {
        if (!pitchers || pitchers.length === 0) return null;

        const section = createElement('div', 'mlb-pitching-section');

        const table = document.createElement('table');
        table.className = 'mlb-pitching-table';

        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headerRow.innerHTML = '<th class="player-col">Pitcher</th><th>IP</th><th>H</th><th>R</th><th>ER</th><th>BB</th><th>SO</th><th>NP</th><th>ERA</th>';
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        pitchers.forEach(p => {
            const row = document.createElement('tr');
            const resultStr = p.result ? ` (${p.result}${p.record ? ', ' + p.record : ''})` : '';
            row.innerHTML = `
                <td class="player-col">${p.name}${resultStr}</td>
                <td>${p.ip}</td><td>${p.h}</td><td>${p.r}</td><td>${p.er}</td><td>${p.bb}</td><td>${p.so}</td><td>${p.np}</td><td>${p.era}</td>
            `;
            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        section.appendChild(table);
        return section;
    };

    // Away team batting
    const awayBatting = renderBattingTable(boxScoreData.away_batting, game.away_team.abbr);
    if (awayBatting) div.appendChild(awayBatting);

    // Away team pitching
    const awayPitching = renderPitchingTable(boxScoreData.away_pitching, game.away_team.abbr);
    if (awayPitching) div.appendChild(awayPitching);

    // Home team batting
    const homeBatting = renderBattingTable(boxScoreData.home_batting, game.home_team.abbr);
    if (homeBatting) div.appendChild(homeBatting);

    // Home team pitching
    const homePitching = renderPitchingTable(boxScoreData.home_pitching, game.home_team.abbr);
    if (homePitching) div.appendChild(homePitching);

    // Game notes (HRs, 2B, 3B, SB, DP)
    const notes = boxScoreData.game_notes;
    if (notes) {
        const notesDiv = createElement('div', 'mlb-game-notes');
        const noteLines = [];

        if (notes.hr && notes.hr.length > 0) {
            noteLines.push(`<strong>HR:</strong> ${notes.hr.join(', ')}`);
        }
        if (notes['2b'] && notes['2b'].length > 0) {
            noteLines.push(`<strong>2B:</strong> ${notes['2b'].join(', ')}`);
        }
        if (notes['3b'] && notes['3b'].length > 0) {
            noteLines.push(`<strong>3B:</strong> ${notes['3b'].join(', ')}`);
        }
        if (notes.sb && notes.sb.length > 0) {
            noteLines.push(`<strong>SB:</strong> ${notes.sb.join(', ')}`);
        }
        if (notes.dp && notes.dp > 0) {
            noteLines.push(`<strong>DP:</strong> ${notes.dp}`);
        }

        if (noteLines.length > 0) {
            notesDiv.innerHTML = noteLines.join(' · ');
            div.appendChild(notesDiv);
        }
    }

    return div;
}

function renderSoccerBoxScore(game, boxScoreData) {
    const div = createElement('div', 'box-score visible soccer-box-score');

    const homeGoals = boxScoreData.home_goals || [];
    const awayGoals = boxScoreData.away_goals || [];

    // Only render if there are goals
    if (homeGoals.length === 0 && awayGoals.length === 0) {
        return div;
    }

    const scorersDiv = createElement('div', 'soccer-scorers');

    // Two-column layout for goal scorers
    const scorersGrid = createElement('div', 'scorers-grid');

    // Away team column
    const awayCol = createElement('div', 'scorers-column');
    awayCol.innerHTML = `<div class="team-label">${game.away_team.abbr}</div>`;
    if (awayGoals.length > 0) {
        awayGoals.forEach(goal => {
            const goalLine = createElement('div', 'soccer-goal');
            let text = `${goal.scorer} ${goal.minute}`;
            if (goal.assist) {
                text += ` <span class="assist">(${goal.assist})</span>`;
            }
            goalLine.innerHTML = text;
            awayCol.appendChild(goalLine);
        });
    } else {
        awayCol.innerHTML += '<div class="no-goals">—</div>';
    }
    scorersGrid.appendChild(awayCol);

    // Home team column
    const homeCol = createElement('div', 'scorers-column');
    homeCol.innerHTML = `<div class="team-label">${game.home_team.abbr}</div>`;
    if (homeGoals.length > 0) {
        homeGoals.forEach(goal => {
            const goalLine = createElement('div', 'soccer-goal');
            let text = `${goal.scorer} ${goal.minute}`;
            if (goal.assist) {
                text += ` <span class="assist">(${goal.assist})</span>`;
            }
            goalLine.innerHTML = text;
            homeCol.appendChild(goalLine);
        });
    } else {
        homeCol.innerHTML += '<div class="no-goals">—</div>';
    }
    scorersGrid.appendChild(homeCol);

    scorersDiv.appendChild(scorersGrid);
    div.appendChild(scorersDiv);

    return div;
}
