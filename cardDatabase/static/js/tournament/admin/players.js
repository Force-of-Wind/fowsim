let players = [];

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
    $.ajax({
        url: `/api/tournament/${getTournamentId()}/render-players/`,
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

$(document).ready(function () {
    $('#remove-player-btn').on('click', removePlayerFromTournament);
});

// Render the player list on page load
document.addEventListener("DOMContentLoaded", fetchPlayersFromAPI);