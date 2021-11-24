$(function() {
    $('.card-quantity-minus').click(function(event){
        $(this).siblings('input').val(function(i, oldVal){
            return Math.max(parseInt(oldVal, 10) - 1, 1);
        });
    });
    $('.card-quantity-plus').click(function(event){
        $(this).siblings('input').val(function(i, oldVal){
            return parseInt(oldVal, 10) + 1;
        });
    });

    $('#save-deck-button').click(function(event){

    });

    $('.deck-zone-card').mouseover(function(event){
        $(this).find('img').addClass('show-hover');
    });

    $('.deck-zone-card').mouseout(function(event){
        $(this).find('img').removeClass('show-hover');
    });
});