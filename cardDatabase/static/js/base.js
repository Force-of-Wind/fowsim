$(function(){
    $('#advanced-search-toggle').on('click',
    function (event){
        $('#basic-search').hide();
        $('#advanced-search').show();
        $('#search-toggles').removeClass('basic-showing');
        $('#search-toggles').addClass('advanced-showing');
    });
    $('#basic-search-toggle').on('click',
        function(event){
            $('#basic-search').show();
            $('#advanced-search').hide();
            $('#search-toggles').addClass('basic-showing');
            $('#search-toggles').removeClass('advanced-showing');
        });
});