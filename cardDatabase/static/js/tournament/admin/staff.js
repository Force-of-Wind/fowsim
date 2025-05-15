
function searchForStaff(e) { 
    let userName = "";
}

function removeStaff(e) { 
    console.log($(e.target).data('id')); 
}

$(document).ready(function () {
    $('#staff-add-btn').on('click', searchForStaff);
    $('#staff-remove-btn').on('click', removeStaff);
});