/* Data Rendering Functions */

// Check if box score has any meaningful data to display
function hasBoxScoreData(boxScore) {
    if (!boxScore) return false;

    // Check for line score with actual values
    const hasLineScore = boxScore.line_score &&
        boxScore.line_score.away &&
        boxScore.line_score.away.length > 0 &&
        boxScore.line_score.away.some(v => v > 0);

    // Check for scorers
    const hasScorers = boxScore.scorers && boxScore.scorers.length > 0;

    // Check for goalies (NHL)
    const hasGoalies = boxScore.goalies && boxScore.goalies.length > 0;

    // Check for shots (NHL)
    const hasShots = boxScore.shots && (boxScore.shots.away > 0 || boxScore.shots.home > 0);

    return hasLineScore || hasScorers || hasGoalies || hasShots;
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

    const section = createElement('section', `league-section league-${leagueKey}`);
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
        section.appendChild(renderYesterdayScores(data.yesterday, prefs.showBoxScores));
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

function renderYesterdayScores(yesterday, showBoxScores) {
    const container = createElement('div', 'yesterday-scores');
    container.setAttribute('role', 'region');
    container.setAttribute('aria-label', "Yesterday's game scores");

    const title = createElement('h3', 'subsection-header', `Yesterday's Scores`);
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
    } else if (leagueKey === 'epl') {
        // EPL doesn't have divisions, just show single table
        const divContainer = createElement('div', 'standings-division');

        const table = document.createElement('table');
        table.className = 'standings-table';
        table.setAttribute('aria-label', 'Premier League standings');

        // Header with spelled-out abbreviations
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headerRow.innerHTML = `
            <th class="rank" scope="col">#</th>
            <th class="team" scope="col">Team</th>
            <th class="numeric" scope="col">Played</th>
            <th class="numeric" scope="col">Wins</th>
            <th class="numeric" scope="col">Draws</th>
            <th class="numeric" scope="col">Losses</th>
            <th class="numeric" scope="col"><abbr title="Goals For">GF</abbr></th>
            <th class="numeric" scope="col"><abbr title="Goals Against">GA</abbr></th>
            <th class="numeric" scope="col"><abbr title="Goal Difference">GD</abbr></th>
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
                <td class="team">${team.team_name || team.team}</td>
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

    // Category display names - only NBA uses "Per Game" (rate stats)
    const categoryLabels = leagueKey === 'nba' ? {
        'points': 'Points Per Game',
        'assists': 'Assists Per Game',
        'rebounds': 'Rebounds Per Game'
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
        const dateObj = new Date(day.date);
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
