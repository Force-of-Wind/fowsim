$(document).ready(function($) {
    $(".date-time-picker").flatpickr({
        enableTime: true,
        altInput: true,
        altFormat: "Y-m-d H:i",
        dateFormat: "Z",
        minDate: "today",
        time_24hr: true,
        allowInput:true,
        onOpen: function(selectedDates, dateStr, instance) {
            $(instance.altInput).prop('readonly', true);
        },
        onClose: function(selectedDates, dateStr, instance) {
            $(instance.altInput).prop('readonly', false);
            $(instance.altInput).blur();
        }
    });

    $('#level').on('change', function (e) {
        let hint = $("option:selected", this).data('hint');

        if(hint?.length > 0)
            $('.level-hint').text(hint);
        else
            $('.level-hint').text('');
    });
    // $('#create-tournament').on('submit', function (event) {
    //     event.preventDefault();
    //     console.log($('#create-tournament').serializeArray());
    // });
});