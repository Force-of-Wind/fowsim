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
            renderPlayers();
        },
        error: function (error) {
            alert('Error fetching players.');
            console.error(error);
        }
    });
}

function savePlayersToAPI() {
    $.ajax({
        url: `/api/tournament/${getTournamentId()}/players/update/`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(players),
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        success: function (response) {
            alert('Players saved successfully!');
        },
        error: function (error) {
            alert('Error saving players.');
            console.error(error);
        }
    });
}

function renderPlayers() {
    let html;

    if (players.length < 1) {
        html = `<h3 class="ml-3"><b>No players registered!</b></h3>`;
        document.getElementById("savePlayersBtn").setAttribute('disabled', true);
        return;
    }

    players.forEach((player, index) => {
        let baseUrl = $('#decklist_detail_url_base').val();
        firstName = escapeHtml(player.userData.filter(e => e.name == 'firstname')[0].value);
        lastName = escapeHtml(player.userData.filter(e => e.name == 'lastname')[0].value);

        additionalInfoFields =  player.userData.filter(e => e.name != 'firstname' && e.name != 'lastname');

        infoFieldsHtml = "";

        additionalInfoFields.forEach(e => {
            infoFieldsHtml += `<strong>${e.label}:</strong><span class="text-wrapper"> ${escapeHtml(e.value)}</span><br>`
        });

        shareLink = baseUrl.replace('0', player.decklistId).replace('changeMe', player.decklistShareCode);
        const card = `
            <div class="col-md-4 mb-3">
                <div class="card ${player.dropped ? 'border-danger' : ''}">
                    <div class="card-body">
                        <h5 class="card-title">${firstName} ${lastName}</h5>
                        <h6 class="card-subtitle text-muted">@${player.username}</h6>
                        <input type="hidden" class="player-id" value="${player.id}">
                        <p class="mt-2">
                            <strong>Standing:</strong> 
                            <input type="number" class="form-control form-control-sm d-inline w-25" 
                                value="${player.standing}" ${window.can_write ? '' : 'disabled'} onchange="updateStanding(${index}, this.value)">
                            <br>
                            <strong>Status:</strong> 
                            <select class="form-control form-control-sm d-inline w-50" ${window.can_write ? '' : 'disabled'}
                                    onchange="updateStatus(${index}, this.value)">
                                <option value="requested" ${player.status === 'requested' ? 'selected' : ''}>Requested</option>
                                <option value="accepted"  ${player.status === 'accepted' ? 'selected' : ''}>Accepted</option>
                                <option value="completed" ${player.status === 'completed' ? 'selected' : ''}>Completed</option>
                            </select>
                            <br>
                            ${player.dropped ? '<span class="text-danger">Dropped Out</span>' : ''}
                            <br>
                            <strong>Notes:</strong>
                            <textarea class="form-control form-control-sm" rows="3" ${window.can_write ? '' : 'disabled'} onchange="updateNotes(${index}, this.value)">${player.notes}</textarea>
                        </p>
                        <a href="#collapse-${player.id}" class="btn btn-outline-primary flex-center mt-1 mb-2" data-toggle="collapse" data-target="#collapse-${player.id}" aria-expanded="true" aria-controls="collapse-${player.id}">
                                Details
                            </a>
                            <div id="accordion-${player.id}">
                                <div id="collapse-${player.id}" class="collapse" data-parent="#accordion-${player.id}">
                                    ${infoFieldsHtml}
                                </div>
                            </div>
                        <a href="${shareLink}" class="btn btn-sm btn-info" target="_blank">View Decklist</a>
                        ${player.dropped ?
                            `<button class="btn btn-sm btn-primary ${window.can_write ? '' : 'disabled'} float-right" onclick="undropPlayer(${index})">
                                Un-Drop Player
                            </button>`:
                            `<button class="btn btn-sm btn-danger ${window.can_write ? '' : 'disabled'} float-right" onclick="dropPlayer(${index})">
                                Drop Player
                            </button>`
                        }
                        
                        ${window.can_delete ?
                            `<br><button class="btn btn-sm btn-danger float-right mt-3" onclick="removePlayer(${index})" data-toggle="modal" data-target="#playerRemoveModal">
                            Remove Player
                        </button>` : ''}
                    </div>
                </div>
            </div>
        `;
        html += card;
    });

    $('#playerList').html(html);
}

function dropPlayer(index) {
    players[index].dropped = true;
    renderPlayers();
}

function undropPlayer(index) {
    players[index].dropped = false;
    renderPlayers();
}

function escapeHtml(string) {
  return $('<div>').text(string).html();
}

function removePlayer(index) {
    let player =  players[index];
    firstName = player.userData.filter(e => e.name == 'firstname')[0].value;
    lastName = player.userData.filter(e => e.name == 'lastname')[0].value;
    
    let name = `${firstName} ${lastName} - ${player.username}`
    $('#remove-player-name').text(name);
    $('#remove-player-id').val(player.id);
}

function removePlayerFromTournament() {
    let playerId = $('#remove-player-id').val();

    console.log(playerId);

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
            alert('Error saving players.');
            console.error(error);
        }
    });
}

function updateStatus(index, newStatus) {
    players[index].status = newStatus;
}

function updateStanding(index, newStanding) {
    players[index].standing = parseInt(newStanding) || 0;
}

function updateNotes(index, newNotes) {
    players[index].notes = newNotes;
}



$(document).ready(function () {
    $('#remove-player-btn').on('click', removePlayerFromTournament);
});

// Render the player list on page load
document.addEventListener("DOMContentLoaded", fetchPlayersFromAPI);