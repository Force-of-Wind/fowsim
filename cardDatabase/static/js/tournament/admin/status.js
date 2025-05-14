const statusOrder = ['created', 'registration', 'swiss', 'tops', 'completed'];

function getTournamentId() {
    return document.getElementById("tournamentId").value;
}

function getCSRFToken() {
    return document.getElementById("csrfToken").value;
}

function translateStatus(status) {
    const translations = {
        'created': 'Tournament Created',
        'registration': 'Registration Open',
        'swiss': 'Swiss Rounds Ongoing',
        'tops': 'Top Cut Rounds',
        'completed': 'Tournament Completed'
    };

    return translations[status] || 'Unknown Status';
}

function disableButtons(currentStatus) {
    document.querySelectorAll('.status-btn').forEach(button => {
        button.disabled = true;
    });

    if (currentStatus === 'created') {
        document.getElementById('createBtn').disabled = false;
    } else if (currentStatus === 'registration') {
        document.getElementById('registrationBtn').disabled = false;
    } else if (currentStatus === 'swiss') {
        document.getElementById('swissBtn').disabled = false;
    } else if (currentStatus === 'tops') {
        document.getElementById('topsBtn').disabled = false;
    }
}

function advanceStatus() {
    const statusInput = document.getElementById('status');
    const currentStatus = statusInput.value;

    const currentIndex = statusOrder.indexOf(currentStatus);

    if (currentIndex < statusOrder.length - 1) {
        const nextStatus = statusOrder[currentIndex + 1];

        document.getElementById('nextStatus').value = nextStatus;
    } else {
        alert('The tournament is already completed!');
    }
}

$(document).ready(function() {
    $('#confirmBtn').on('click', function() {
        const nextStatus = document.getElementById('nextStatus').value;
        const statusInput = document.getElementById('status');

        statusInput.value = nextStatus;
        document.getElementById('currentStatus').innerText = `Current Phase: ${translateStatus(nextStatus)}`;

        $.ajax({
            url: `/api/tournament/${getTournamentId()}/phase/update/`,
            type: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
            data: {
                status: nextStatus
            },
            success: function(response) {
                
                $('#confirmModal').modal('hide');

                disableButtons(nextStatus);
            },
            error: function(error) {
                console.error('Error updating status:', error);
                alert('There was an error updating the status. Please try again later.');
            }
        });
    });

    function revealDecklists(reveal = false) {
        let data = {};
        if(reveal)
            data.revealState = true;

        $.ajax({
            url: `/api/tournament/${getTournamentId()}/decklist/reveal/update/`,
            type: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
            data: data,
            success: function(_) {
                window.location.reload();
            },
            error: function(error) {
                console.error('Error updating decklist reveal status:', error);
                alert('There was an error updating the decklist reveal status. Please try again later.');
            }
        });
    }

    function resetPhase() { 
        $.ajax({
            url: `/api/tournament/${getTournamentId()}/reset/phase`,
            type: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
            data: {},
            success: function(_) {
                window.location.reload();
            },
            error: function(error) {
                console.error('Error resetting phase:', error);
                alert('There was an error resetting the tournaments phase. Please try again later.');
            }
        });
    }

    function lockDecklistEdit(lock = true) {
        let data = {};
        if(lock)
            data.lockState = true;
        
        $.ajax({
            url: `/api/tournament/${getTournamentId()}/lock/deck-edit`,
            type: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
            data: data,
            success: function(_) {
                window.location.reload();
            },
            error: function(error) {
                console.error('Error resetting phase:', error);
                alert('There was an error resetting the tournaments phase. Please try again later.');
            }
        });
    }

    $('.status-btn').on('click', advanceStatus);

    $('#reveal-decklists-btn').on('click', function(e){
        revealDecklists(true);
    });

    $('#hide-decklists-btn').on('click', function(e){
        revealDecklists(false);
    });

    $('#lock-decklist-edit-btn').on('click',function(e) {
        lockDecklistEdit(true);
    });

    $('#unlock-decklist-edit-btn').on('click',function(e) {
        lockDecklistEdit(false);
    });

    $('#reset-phase').on('click', resetPhase)

    $('.local-date-time').each(function() {
        if(!$(this).data('epoch'))
            return;

        //use epoch to increase time
        var dateTime = new Date(0); 
        dateTime.setUTCSeconds($(this).data('epoch'));
        $(this).text(dateTime.toLocaleString());
    });

    disableButtons(document.getElementById('status').value);

    document.getElementById('currentStatus').innerText = `Current Phase: ${translateStatus(document.getElementById('status').value)}`;
});
