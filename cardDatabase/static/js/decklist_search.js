$(function() {
    //localize date times
    $('.local-date-time').each(function() {
         if(!$(this).data('epoch'))
             return;
 
         //use epoch to increase time
         var dateTime = new Date(0); 
         dateTime.setUTCSeconds($(this).data('epoch'));
         $(this).text(dateTime.toLocaleString());
     })
 });