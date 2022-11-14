$(function(){
    $('.pick-title').on('click', function(event){
        $('.pick-title.active-pick').removeClass('active-pick');
        $(this).addClass('active-pick');

        $('.pick-period-content.active-pick').removeClass('active-pick');
        $('#pick-period-' + $(this).data('css-id')).addClass('active-pick');
    })
});