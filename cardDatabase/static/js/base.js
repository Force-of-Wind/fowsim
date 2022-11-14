$(function(){
    if (!FOWDB_IS_MOBILE) {
        $('.referenced-card').mouseover(function (event) {
            $(this).find('img').addClass('show-hover');
            $(this).find('.multi-hovered-img').addClass('show-hover');
        });

        $('.referenced-card').mouseout(function (event) {
            $(this).find('img').removeClass('show-hover');
            $(this).find('.multi-hovered-img').removeClass('show-hover');
        });
    }
});