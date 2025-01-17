$(document).ready(function($) {
    $(".date-time-picker").flatpickr({
        enableTime: true,
        altInput: true,
        altFormat: "Y-m-d H:i",
        dateFormat: "Z",
        minDate: "today",
        time_24hr: true
    });
});