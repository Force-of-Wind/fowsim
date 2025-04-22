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
        success: function(response) {
            players = response;
            renderPlayers();
        },
        error: function(error) {
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
        data: JSON.stringify(players) ,
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        success: function(response) {
            alert('Players saved successfully!');
            console.log(response);
        },
        error: function(error) {
            alert('Error saving players.');
            console.error(error);
        }
    });
}

function renderPlayers() {
    const playerList = document.getElementById("playerList");
    playerList.innerHTML = "";

    if (players.length < 1)
    {
        playerList.innerHTML = `<h3 class="ml-3"><b>No players registered!</b></h3>`;
        document.getElementById("savePlayersBtn").setAttribute('disabled', true);
        return;
    }

    players.forEach((player, index) => {
        const card = `
            <div class="col-md-4 mb-3">
                <div class="card ${player.dropped ? 'border-danger' : ''}">
                    <div class="card-body">
                        <h5 class="card-title">${player.firstName} ${player.lastName}</h5>
                        <h6 class="card-subtitle text-muted">@${player.username}</h6>
                        <input type="hidden" class="player-id" value="${player.id}">
                        <p class="mt-2">
                            <strong>Standing:</strong> 
                            <input type="number" class="form-control form-control-sm d-inline w-25" 
                                value="${player.standing}" onchange="updateStanding(${index}, this.value)">
                            <br>
                            <strong>Status:</strong> 
                            <select class="form-control form-control-sm d-inline w-50" 
                                    onchange="updateStatus(${index}, this.value)">
                                <option value="requested" ${player.status === 'requested' ? 'selected' : ''}>Requested</option>
                                <option value="accepted" ${player.status === 'accepted' ? 'selected' : ''}>Accepted</option>
                                <option value="completed" ${player.status === 'completed' ? 'selected' : ''}>Completed</option>
                            </select>
                            <br>
                            ${player.dropped ? '<span class="text-danger">Dropped Out</span>' : ''}
                            <br>
                            <strong>Notes:</strong>
                            <textarea class="form-control form-control-sm" rows="3" onchange="updateNotes(${index}, this.value)">${player.notes}</textarea>
                        </p>
                        <a href="${player.decklist}" class="btn btn-sm btn-info" target="_blank">View Decklist</a>
                        <button class="btn btn-sm btn-danger float-right" onclick="dropPlayer(${index})">
                            Drop Player
                        </button>
                    </div>
                </div>
            </div>
        `;
        playerList.innerHTML += card;
    });
}

function dropPlayer(index) {
    players[index].dropped = true;
    renderPlayers();
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

// Render the player list on page load
document.addEventListener("DOMContentLoaded", fetchPlayersFromAPI);