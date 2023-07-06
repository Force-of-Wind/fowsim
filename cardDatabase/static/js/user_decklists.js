$(function() {
   $('.delete-deck-button').on('click', function(event){
       if (!(confirm(`Are you sure you want to delete deck: ${$(this).parents('tr').data('decklist-name')}? This cannot be undone`))){
           return;
       }
       let deck_pk = $(this).parents('tr').data('decklist-pk');
       $.ajax({
           type: 'POST',
           url: `/delete_decklist/${deck_pk}/`,
           success: function(data){
               window.location.reload();
           },
           error: function(data){
               console.log('Error');
           },
       })
   });

   $('.share-deck-button').on('click', function(event){
       let deck_url = $(this).parents('tr').find(`.view-deck-button a`).attr('href');
       const elem = document.createElement('textarea');
       elem.value = window.location.origin + deck_url;
       document.body.appendChild(elem);
       elem.select();
       document.execCommand('copy');
       document.body.removeChild(elem);
       alert('Link copied');
   });

   if (FOWDB_IS_MOBILE){
       // Convert the name hyperlink to the whole row
       $('#user-decklists tr.deck-info').click(function(event){
          let dest = $(this).find('a').attr('href');
          window.location.assign(dest);
       });
   }

   if (!FOWDB_IS_MOBILE){
       $('body').addClass('hasHover');
   }

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