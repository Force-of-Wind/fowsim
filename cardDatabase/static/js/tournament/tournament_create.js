$(document).ready(function($) {
    $(".date-time-picker").flatpickr({
        enableTime: true,
        altInput: true,
        altFormat: "Y-m-d H:i",
        dateFormat: "Z",
        minDate: "today",
        time_24hr: true
    });

    $('#level').on('change', function (e) {
        let hint = $("option:selected", this).data('hint');

        if(hint?.length > 0)
            $('.level-hint').text(hint);
        else
            $('.level-hint').text('');
    });

    const defaultFields = {
        localtion: {
            label:'Location',
            maxlength:'200',
            type:'text',
            name:'location',
            class:'form-control'
        },
        prices: {
            label:'Prices',
            maxlength:'200',
            type:'text',
            name:'prices',
            class:'form-control'
        },
        pricesLink: {
            label:'Prices Link',
            maxlength:'200',
            type:'text',
            name:'prices-link',
            class:'form-control'
        },
        fee: {
            label:'Tournament Fee',
            maxlength:'200',
            type:'text',
            name:'fee',
            class:'form-control'
        },
        additionalInfo: {
            label:'Additional Info',
            maxlength:'500',
            type:'textarea',
            name:'additional-info',
            class:'form-control'
        },
    };
});