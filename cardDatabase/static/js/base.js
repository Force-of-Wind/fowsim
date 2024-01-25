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

    /*
    Sets all divs with the data attributes localizable-dt to have the text value equal to the user's timezone
    localizable-dt: an epoch second
     */
    $("div[data-localizable-dt]").each(function(i, obj){
        let dt = new Date($(this).data('localizable-dt') * 1000); // JS uses milliseconds, Py uses seconds
        let dt_string = dt.toLocaleString();
        $(this).text(dt_string);
    })
});