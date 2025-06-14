/* TODO this is more or less already done in base.js to all pages. We could just add an attribute flag to choose whether to use ISO string or DateString
*/
$(function () {
    $('.local-date-time').each(function() {
        if(!$(this).data('epoch'))
            return;

        let isoString = false;

        if($(this).data('iso-date'))
            isoString = true;
    
        //use epoch to increase time
        var dateTime = new Date(0); 
        dateTime.setUTCSeconds($(this).data('epoch'));

        if(isoString){
            $(this).text(dateTime.toISOString());
            $(this).val(dateTime.toISOString());
        }
        else{
            $(this).text(dateTime.toLocaleString());
            $(this).val(dateTime.toLocaleString());
        }
    });
});