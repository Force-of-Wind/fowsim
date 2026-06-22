let players = [];
let showAsTable = false;
let showAsBoxes = false;

function getTournamentId() {
    return document.getElementById("tournamentId").value;
}

function getCSRFToken() {
    return document.getElementById("csrfToken").value;
}

/* =========================================================
   Fetching / rendering
   ========================================================= */
function fetchPlayersFromAPI() {
    $.ajax({
        url: `/api/tournament/${getTournamentId()}/players/`,
        type: 'GET',
        dataType: 'json',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        success: function (response) {
            players = response;
            updatePlayerCountBadge();
            fetchPlayersHTMLFromAPI();
            setupRulersForStats(players);
            drawStatsForRulers();
        },
        error: function (error) {
            alertify.error('Error fetching players!');
            console.error(error);
        }
    });
}

function fetchPlayersHTMLFromAPI() {
    let queryParam = '';
    if(!showAsBoxes && showAsTable)
        queryParam = '?asTable=true'
    $.ajax({
        url: `/api/tournament/${getTournamentId()}/render-players/${queryParam}`,
        type: 'GET',
        dataType: 'html',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        success: function (response) {
            renderPlayers(response);
        },
        error: function (error) {
            alertify.error('Error fetching players!');
            console.error(error);
        }
    });
}

function renderPlayers(html) {
    if(showAsBoxes && !showAsTable){
        if($('#playerList').hasClass('table-responsive')){
            $('#playerList').removeClass('table-responsive');
            $('#playerList').addClass('row');
        }
    }
    else if(!showAsBoxes && showAsTable){
        if($('#playerList').hasClass('row')){
            $('#playerList').removeClass('row');
            $('#playerList').addClass('table-responsive');
        }
    }

    $('#playerList').html(html);

    // Drag-to-reorder is only offered in the table view.
    if(showAsTable && !showAsBoxes)
        initStandingsSortable();
}

function updatePlayerCountBadge() {
    $('#player-count-badge').text(players.length);
}

/* =========================================================
   Auto-save
   ========================================================= */
let autosaveTimer = null;

function setAutosaveIndicator(state) {
    const $ind = $('#autosave-indicator');
    $ind.removeClass('saving saved error');
    if(state === 'saving'){
        $ind.addClass('saving').text('Saving…');
    } else if(state === 'saved'){
        $ind.addClass('saved').text('All changes saved');
        clearTimeout(autosaveTimer);
        autosaveTimer = setTimeout(() => $ind.text(''), 2500);
    } else if(state === 'error'){
        $ind.addClass('error').text('Save failed');
    } else {
        $ind.text('');
    }
}

// Persist a list of player objects to the bulk update endpoint.
// Returns the jqXHR so callers can chain.
function persistPlayers(playerList) {
    if(!window.can_write){
        return null;
    }
    if(!playerList || playerList.length < 1){
        return null;
    }

    setAutosaveIndicator('saving');

    return $.ajax({
        url: `/api/tournament/${getTournamentId()}/players/update/`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(playerList),
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        success: function () {
            setAutosaveIndicator('saved');
        },
        error: function (error) {
            setAutosaveIndicator('error');
            alertify.error('Could not save changes');
            console.error(error);
        }
    });
}

function autosavePlayer(player) {
    if(!player) return;
    persistPlayers([player]);
}

// Manual full save (kept for compatibility / fallback).
function savePlayersToAPI() {
    if(players.length < 1){
        alertify.error('No players to save!');
        return;
    }
    persistPlayers(players);
}

/* =========================================================
   Per-field edits (called from inline onchange handlers)
   ========================================================= */
function updateStatus(id, newStatus) {
    let player = getPlayerById(id);
    if(!player) return;
    player.status = newStatus;
    autosavePlayer(player);
}

function updateStanding(id, newStanding) {
    let player = getPlayerById(id);
    if(!player) return;
    player.standing = parseInt(newStanding) || 0;
    autosavePlayer(player);
}

let notesSaveTimers = {};
function updateNotes(id, newNotes) {
    let player = getPlayerById(id);
    if(!player) return;
    player.notes = newNotes;
    // Debounce in case this is wired to keystrokes; harmless on blur-only.
    clearTimeout(notesSaveTimers[id]);
    notesSaveTimers[id] = setTimeout(() => autosavePlayer(player), 600);
}

function getPlayerById(id){
    return players.filter(e => e.id == id)[0];
}

/* =========================================================
   Drop / un-drop
   ========================================================= */
function dropPlayer(id) {
    let player = getPlayerById(id);
    if(!player) return;
    player.dropped = true;
    changeDropStatus(player, true);
    autosavePlayer(player);
}

function undropPlayer(id) {
    let player = getPlayerById(id);
    if(!player) return;
    player.dropped = false;
    changeDropStatus(player, false);
    autosavePlayer(player);
}

function changeDropStatus(player, dropStatus) {
    if(dropStatus){
        if(!$(`#card-${player.id}`).hasClass('border-danger'))
            $(`#card-${player.id}`).addClass('border-danger');

        if(!$(`#drop-${player.id}`).hasClass('hidden'))
            $(`#drop-${player.id}`).addClass('hidden');

        if($(`#undrop-${player.id}`).hasClass('hidden'))
            $(`#undrop-${player.id}`).removeClass('hidden');
    }
    else{
        if($(`#card-${player.id}`).hasClass('border-danger'))
            $(`#card-${player.id}`).removeClass('border-danger');

        if(!$(`#undrop-${player.id}`).hasClass('hidden'))
            $(`#undrop-${player.id}`).addClass('hidden');

        if($(`#drop-${player.id}`).hasClass('hidden'))
            $(`#drop-${player.id}`).removeClass('hidden');
    }
}

/* =========================================================
   Remove player
   ========================================================= */
function removePlayer(id) {
    let player = getPlayerById(id);
    let name = `${player.firstname} ${player.lastname} - ${player.username}`
    $('#remove-player-name').text(name);
    $('#remove-player-id').val(player.id);
}

function removePlayerFromTournament() {
    let playerId = $('#remove-player-id').val();
    if (!playerId)
        return;

    $.ajax({
        url: `/api/tournament/${getTournamentId()}/players/remove/${playerId}/`,
        type: 'POST',
        contentType: 'application/json',
        data: {},
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        success: function () {
            fetchPlayersFromAPI();
        },
        error: function (error) {
            alertify.error('Error removing player!');
            console.error(error);
        }
    });
}

/* =========================================================
   Drag-to-reorder standings (table view)
   ========================================================= */
function initStandingsSortable() {
    if(!window.can_write) return;

    let $tbody = $('#playerList table tbody');
    if(!$tbody.length || typeof $tbody.sortable !== 'function') return;

    if($tbody.hasClass('ui-sortable'))
        $tbody.sortable('destroy');

    $tbody.sortable({
        items: 'tr.standing-row',
        handle: '.drag-handle',
        axis: 'y',
        placeholder: 'standing-placeholder',
        helper: function (e, tr) {
            // Keep column widths while dragging.
            let $originals = tr.children();
            let $helper = tr.clone();
            $helper.children().each(function (index) {
                $(this).width($originals.eq(index).width());
            });
            return $helper;
        },
        update: function () {
            applyStandingsFromTableOrder();
        }
    });
}

function applyStandingsFromTableOrder() {
    let changed = [];
    $('#playerList table tbody tr.standing-row').each(function (index) {
        let id = $(this).data('id');
        let newStanding = index + 1;

        // Reflect the new standing in the row UI.
        $(this).find('.standing-display').text(newStanding);
        $(this).find('input[name="standing"]').val(newStanding);

        let player = getPlayerById(id);
        if(player && player.standing !== newStanding){
            player.standing = newStanding;
            changed.push(player);
        }
    });

    if(changed.length)
        persistPlayers(changed);
}

/* =========================================================
   Cross-tournament notes (judging) — Admin / Owner only
   ========================================================= */
function escapeHtml(value) {
    return $('<div>').text(value == null ? '' : value).html();
}

function loadOtherNotes(playerId) {
    $('#other-notes-title').text('');
    $('#other-notes-body').html('<p class="text-muted">Loading…</p>');

    $.ajax({
        url: `/api/tournament/${getTournamentId()}/players/${playerId}/other-notes/`,
        type: 'GET',
        dataType: 'json',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        success: function (response) {
            renderOtherNotes(response);
        },
        error: function (error) {
            $('#other-notes-body').html('<p class="text-danger">Could not load notes from other tournaments.</p>');
            console.error(error);
        }
    });
}

function renderOtherNotes(response) {
    $('#other-notes-title').text(`${response.playerName} (@${response.username})`);

    if(!response.notes || response.notes.length === 0){
        $('#other-notes-body').html('<p class="text-muted">No notes found in other tournaments.</p>');
        return;
    }

    let html = '';
    response.notes.forEach(note => {
        let meta = `Standing ${note.standing}` + (note.droppedOut ? ', dropped out' : '');
        html += `<div class="other-note">`
            + `<div class="other-note-header">`
            + `<strong>${escapeHtml(note.tournament)}</strong>`
            + ` <span class="text-muted">— ${escapeHtml(meta)}</span>`
            + `</div>`
            + `<div class="other-note-body">${escapeHtml(note.notes)}</div>`
            + `</div>`;
    });

    $('#other-notes-body').html(html);
}

/* =========================================================
   Import standings by name
   ========================================================= */
function normalizeName(value) {
    let v = (value || '').trim().toLowerCase();
    if(v.startsWith('@'))
        v = v.substring(1);
    return v;
}

// Tiered matching: username -> full name -> first/last name.
// Returns { type: 'matched'|'ambiguous'|'unmatched', player?, count }
function findPlayersForName(rawName) {
    let q = normalizeName(rawName);
    if(!q) return { type: 'unmatched', count: 0 };

    const tiers = [
        p => normalizeName(p.username) === q,
        p => `${(p.firstname||'').trim()} ${(p.lastname||'').trim()}`.trim().toLowerCase() === q,
        p => (p.firstname||'').trim().toLowerCase() === q || (p.lastname||'').trim().toLowerCase() === q,
    ];

    for(const predicate of tiers){
        let hits = players.filter(predicate);
        if(hits.length === 1)
            return { type: 'matched', player: hits[0], count: 1 };
        if(hits.length > 1)
            return { type: 'ambiguous', count: hits.length };
    }
    return { type: 'unmatched', count: 0 };
}

let importPlan = []; // [{ player, standing }] — matched players with their pasted line number

function previewImportStandings() {
    let raw = $('#import-standings-text').val() || '';
    let lines = raw.split('\n').map(l => l.trim()).filter(l => l.length > 0);

    importPlan = [];
    let usedIds = new Set();
    let html = '';
    let matchedCount = 0, problemCount = 0;

    lines.forEach((line, i) => {
        let result = findPlayersForName(line);
        let cls = 'import-line--unmatched';
        let resultText = 'No match';

        if(result.type === 'matched'){
            if(usedIds.has(result.player.id)){
                cls = 'import-line--ambiguous';
                resultText = `Already matched on an earlier line (@${result.player.username})`;
                problemCount++;
            } else {
                cls = 'import-line--matched';
                resultText = `→ ${result.player.firstname} ${result.player.lastname} (@${result.player.username})`;
                usedIds.add(result.player.id);
                // Store the pasted line number so the standing reflects the
                // finishing position the organiser typed, not the position in
                // the matched-only plan. Skipped lines then leave a gap instead
                // of shifting every following player's standing down by one.
                importPlan.push({ player: result.player, standing: i + 1 });
                matchedCount++;
            }
        } else if(result.type === 'ambiguous'){
            cls = 'import-line--ambiguous';
            resultText = `Ambiguous — matches ${result.count} players, skipped`;
            problemCount++;
        } else {
            problemCount++;
        }

        html += `<div class="import-line ${cls}">`
            + `<span class="import-line-num">${i + 1}.</span>`
            + `<span class="import-line-name">${$('<div>').text(line).html()}</span>`
            + `<span class="import-line-result">${$('<div>').text(resultText).html()}</span>`
            + `</div>`;
    });

    if(lines.length === 0){
        $('#import-standings-result').html('<em>Paste some names above, then preview.</em>');
        $('#import-standings-apply-btn').prop('disabled', true);
        return;
    }

    let summary = `<div class="import-result-summary">`
        + `<span class="badge badge-success">${matchedCount} matched</span>`
        + (problemCount ? `<span class="badge badge-warning">${problemCount} need attention</span>` : '')
        + `</div>`;

    $('#import-standings-result').html(summary + html);
    $('#import-standings-apply-btn').prop('disabled', matchedCount === 0);
}

function applyImportStandings() {
    if(!importPlan.length){
        alertify.error('Nothing to apply — preview first.');
        return;
    }

    let changed = [];
    importPlan.forEach(planned => {
        let player = getPlayerById(planned.player.id);
        let newStanding = planned.standing;
        if(player && player.standing !== newStanding){
            player.standing = newStanding;
            changed.push(player);
        }
    });

    if(!changed.length){
        alertify.message('Standings already match the imported order.');
        $('#importStandingsModal').modal('hide');
        return;
    }

    let request = persistPlayers(changed);
    if(request){
        request.done(function () {
            alertify.success(`Updated standings for ${changed.length} player(s).`);
            $('#importStandingsModal').modal('hide');
            fetchPlayersFromAPI();
        });
    }
}

/* =========================================================
   Stats helpers
   ========================================================= */
function setupRulersForStats(players)
{
    if(players.length < 1){
        window.rulers = [];
        return;
    }

    let rulers = {}
    let allRulers = players.map(e => e.ruler);

    for (const ruler of allRulers) {
        rulers[ruler] = (rulers[ruler] || 0) + 1;
    }

    window.rulers = rulers;
}

/* =========================================================
   View toggle
   ========================================================= */
function showPlayersAsBoxes(){
    if(showAsBoxes && !showAsTable)
        return;

    showAsBoxes = true;
    showAsTable = false;

    updateButtonClass('#player-as-table-btn', '#player-as-boxes-btn');

    fetchPlayersFromAPI();
}

function showPlayersAsTable(){
    if(showAsTable && !showAsBoxes)
        return;

    showAsTable = true;
    showAsBoxes = false;

    updateButtonClass('#player-as-boxes-btn', '#player-as-table-btn');

    fetchPlayersFromAPI();
}

function updateButtonClass(outlineBtn, normalBtn) {
    if($(outlineBtn).hasClass('btn-info')){
        $(outlineBtn).removeClass('btn-info');
        $(outlineBtn).addClass('btn-outline-info');
    }

    if($(normalBtn).hasClass('btn-outline-info')){
        $(normalBtn).removeClass('btn-outline-info');
        $(normalBtn).addClass('btn-info');
    }
}

/* =========================================================
   CSV export
   ========================================================= */
function exportPlayersToCSV(){
    if(!players){
        return;
    }

    let header = Object.keys(players[0]);
    let data = players.map(e => Object.values(e));
    let finalData = [];
    let headerToRemove = [];

    for (let i = 0; i < data.length; i++) {
        let row = data[i];
        let rowData = [];
        let extraFields = [];
        for (let x = 0; x < row.length; x++) {
            let col = row[x];
            if(typeof col !== "object"){
                rowData.push(col);
            }
            else if(Object.values(col).length > 0){
                if(!headerToRemove.includes(header.at(x)))
                    headerToRemove.push(header.at(x));
                let detailData = Object.values(col);
                for (let z = 0; z < detailData.length; z++) {
                    let detailField = detailData[z];
                    if(detailField?.name && detailField?.value){
                        extraFields.push(detailField.value);
                        if(!header.includes(detailField.name))
                            header.push(detailField.name);
                    }
                }
            }
        }
        rowData.push(...extraFields);
        finalData.push(rowData);
    }

    header = header.filter(e => !headerToRemove.includes(e));

    window.CsvGenerator.setHeaders(header);
    window.CsvGenerator.setData(finalData);
    window.CsvGenerator.download("players.csv");
}

$(document).ready(function () {
    $('#remove-player-btn').on('click', removePlayerFromTournament);
    $('#player-as-boxes-btn').on('click', showPlayersAsBoxes);
    $('#player-as-table-btn').on('click', showPlayersAsTable);
    $('#import-standings-preview-btn').on('click', previewImportStandings);
    $('#import-standings-apply-btn').on('click', applyImportStandings);
});

// Render the player list on page load
document.addEventListener("DOMContentLoaded", fetchPlayersFromAPI);
