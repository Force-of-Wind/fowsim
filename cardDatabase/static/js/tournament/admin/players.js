let players = [];
let showAsTable = false;
let showAsBoxes = false;

function getTournamentId() {
    return document.getElementById("tournamentId").value;
}

function getCSRFToken() {
    return document.getElementById("csrfToken").value;
}

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
            html = response;
            renderPlayers(html);
        },
        error: function (error) {
            alertify.error('Error fetching players!');
            console.error(error);
        }
    });
}

function savePlayersToAPI() {
    if(players.length < 1){
        alertify.error('No players to save!');
        return;
    }
        
    $.ajax({
        url: `/api/tournament/${getTournamentId()}/players/update/`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(players),
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        success: function (response) {
            alertify.success(`Players saved successfully!`);
        },
        error: function (error) {
            alertify.error('Error saving players');
            console.error(error);
        }
    });
}

function renderPlayers(html) {
    if(showAsBoxes && !showAsTable){
        if($('#playerList').hasClass('table-responsive')){
            $('#playerList').removeClass('table-responsive');
            $('#playerList').removeClass('row');
        }
    }
    else if(!showAsBoxes && showAsTable){
        if($('#playerList').hasClass('row')){
            $('#playerList').removeClass('row');
            $('#playerList').removeClass('table-responsive');
        }
    }

    $('#playerList').html(html);
}

function getPlayerById(id){
    return players.filter(e => e.id == id)[0];
}

function dropPlayer(id) {
    player = getPlayerById(id);
    player.dropped = true;
    changeDropStatus(player, true);
}

function undropPlayer(id) {
    player = getPlayerById(id);
    player.dropped = false;
    changeDropStatus(player, false);
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

function removePlayer(id) {
    let player =  getPlayerById(id);
    
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
        success: function (response) {
            fetchPlayersFromAPI();
        },
        error: function (error) {
            alertify.error('Error removing player!');
            console.error(error);
        }
    });
}

function updateStatus(id, newStatus) {
    player = getPlayerById(id);
    player.status = newStatus;
}

function updateStanding(id, newStanding) {
    player = getPlayerById(id);
    player.standing = parseInt(newStanding) || 0;
}

function updateNotes(id, newNotes) {
    player = getPlayerById(id);
    player.notes = newNotes;
}

function setupRulersForStats(players) 
{ 
    if(players.length < 1){
        window.rulers = [];
        return;
    }

    rulers = {}
    allRulers = players.map(e => e.ruler);

    for (const ruler of allRulers) {
        rulers[ruler] = (rulers[ruler] || 0) + 1;
    }

    window.rulers = rulers;
}

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

function exportPlayersToCSV(){
    if(!players){
        return;
    }

    let header = Object.keys(players[0]);

    let data = players.map(e => Object.values(e));

    let finalData = [];

    let headerToRemove = [];

    for (let i = 0; i < data.length; i++) {
        row = data[i];
        let rowData = [];
        let extraFields = [];
        for (let x = 0; x < row.length; x++) {
            col = row[x];
            if(typeof col !== "object"){
                rowData.push(col);
            }
            else if(Object.values(col).length > 0){
                if(!headerToRemove.includes(header.at(x)))
                    headerToRemove.push(header.at(x));
                let detailData = Object.values(col);
                for (let z = 0; z < detailData.length; z++) {
                    detailField = detailData[z];
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

    console.log(headerToRemove);

    header = header.filter(e => !headerToRemove.includes(e));

    window.CsvGenerator.setHeaders(header);
    window.CsvGenerator.setData(finalData);
    window.CsvGenerator.download("players.csv");
}

function mapComplexData(column, header, data) { 
    if(typeof column !== "object")
        return column;

    return column.map(x => `${x.name}=${x.value}`).join(' ')
}

$(document).ready(function () {
    $('#remove-player-btn').on('click', removePlayerFromTournament);
    $('#player-as-boxes-btn').on('click', showPlayersAsBoxes);
    $('#player-as-table-btn').on('click', showPlayersAsTable);
});

// Render the player list on page load
document.addEventListener("DOMContentLoaded", fetchPlayersFromAPI);