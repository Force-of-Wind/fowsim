$(function() {
   $('.delete-deck-button').on('click', function(event){
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
});