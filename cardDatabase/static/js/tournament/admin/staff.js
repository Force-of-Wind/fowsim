function getTournamentId() {
    return document.getElementById("tournamentId").value;
}

function getCSRFToken() {
    return document.getElementById("csrfToken").value;
}

function resetErrorField(){
    $('#staff-error').text('');
    if(!$('#staff-error').hasClass('d-none'))
        $('#staff-error').addClass('d-none')
}


function showError(error) { 
    $('#staff-error').text(error);
    if($('#staff-error').hasClass('d-none'))
        $('#staff-error').removeClass('d-none')
}

function searchForStaff(e) { 
    resetErrorField();

    let userName = $('#staff-name-search').val();
    let staffRole = $('#staff-role-select').val();

    if(!userName){
        showError('Username cannot be empty!');
        return;
    }

    if(staffRole <= 0){
        showError('Role cannot be empty!');
        return;
    }

    $.ajax({
        url: `/api/tournament/${getTournamentId()}/staff/add/`,
        type: 'POST',
        data: { userName: userName, role:staffRole },
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        success: function (response) {
            window.location.reload();
        },
        error: function (error) {
            showError(error?.responseJSON?.error ?? 'Unknown Error');
        }
    });
}

function removeStaff(e) { 
    let pk = $(e.target).data('id');
    $.ajax({
        url: `/api/tournament/${getTournamentId()}/staff/remove/`,
        type: 'POST',
        data: { key: pk },
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        success: function (response) {
            window.location.reload();
        },
        error: function (error) {
            showError(error?.responseJSON?.error ?? 'Unknown Error');
        }
    });
}

$(document).ready(function () {
    $('#staff-add-btn').on('click', searchForStaff);
    $('#staff-remove-btn').on('click', removeStaff);
});