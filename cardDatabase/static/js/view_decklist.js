$(function(){
   $('.deck-card-img').click(function(event){
       $(this).siblings('.card-preview').addClass('show');
   });

    $(document).keyup(function(e){
        if (e.key === "Escape"){
            $('.card-preview').removeClass('show');
        }
    });

    $('.card-preview').click(function(e){
        if (e.target.classList.contains('card-preview')){
            $(this).removeClass('show');
        }
    });

    if (!FOWDB_IS_MOBILE) {
        $('.referenced-card').mouseover(function (event) {
            $(this).find('img').addClass('show-hover');
        });

        $('.referenced-card').mouseout(function (event) {
            $(this).find('img').removeClass('show-hover');
        });
    }
});