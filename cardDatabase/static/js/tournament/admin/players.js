let players = [
    { id: 1, username: "player1", firstName: "John", lastName: "Doe", decklist: "#", status: "accepted", standing: 1, dropped: false, notes: "" },
    { id: 2, username: "player2", firstName: "Jane", lastName: "Smith", decklist: "#", status: "requested", standing: 2, dropped: false, notes: "" },
    { id: 3, username: "player3", firstName: "Alice", lastName: "Johnson", decklist: "#", status: "completed", standing: 3, dropped: true, notes: "" },
    { id: 4, username: "player4", firstName: "Bob", lastName: "Brown", decklist: "#", status: "accepted", standing: 4, dropped: false, notes: "" },
    { id: 5, username: "player5", firstName: "Charlie", lastName: "Williams", decklist: "#", status: "requested", standing: 5, dropped: false, notes: "" },
    { id: 6, username: "player6", firstName: "Diana", lastName: "Miller", decklist: "#", status: "completed", standing: 6, dropped: false, notes: "" },
    { id: 7, username: "player7", firstName: "Ethan", lastName: "Davis", decklist: "#", status: "accepted", standing: 7, dropped: false, notes: "" },
    { id: 8, username: "player8", firstName: "Fiona", lastName: "Garcia", decklist: "#", status: "requested", standing: 8, dropped: true, notes: "" },
    { id: 9, username: "player9", firstName: "George", lastName: "Martinez", decklist: "#", status: "completed", standing: 9, dropped: false, notes: "" },
    { id: 10, username: "player10", firstName: "Hannah", lastName: "Anderson", decklist: "#", status: "accepted", standing: 10, dropped: false, notes: "" }
];

function getTournamentId() {
    return document.getElementById("tournamentId").value;
}

function getCSRFToken() {
    return document.getElementById("csrfToken").value;
}

function fetchPlayersFromAPI() {
    $.ajax({
        url: `/api/get-tournament/players/${getTournamentId()}/`,
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
        url: `/api/tournament-save-players/${getTournamentId()}/`, // Replace with your actual API endpoint
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(players),
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
document.addEventListener("DOMContentLoaded", renderPlayers);