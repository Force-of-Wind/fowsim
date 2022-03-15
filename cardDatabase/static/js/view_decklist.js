$(function(){
   $('.deck-card-img').click(function(event){
       $(this).siblings('.card-preview').addClass('show');
   });

   $('.close-preview').click(function(event){
       $(this).parent().removeClass('show');
   });

    $(document).keyup(function(e){
        if (e.key === "Escape"){
            $('.card-preview').removeClass('show');
        }
    });

    $('.card-preview').click(function(e){
        if (e.target.classList.contains('card-preview')){
            $('.close-preview').trigger('click');
        }
    })
});