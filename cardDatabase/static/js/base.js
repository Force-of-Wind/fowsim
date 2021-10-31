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

    $('.sets-select .mdb-select').materialSelect({
        'visibleOptions': 14,
        'placeholder': 'Search Set(s)...',
        'maxSelectedOptions': 2
    });
    $('.card-type-select .mdb-select').materialSelect({
        'visibleOptions': 14,
        'placeholder': 'Search Card Type(s)...',
        'maxSelectedOptions': 2
    });
    $('.rarity-select .mdb-select').materialSelect({
        'visibleOptions': 14,
        'placeholder': 'Search Rarity(s)...',
        'maxSelectedOptions': 2
    });

    $('.select-text-exactness input, .select-sort-by input').change(function(){
        //Act like radio buttons, uncheck all the other ones in this form field
        if (this.checked){
            $(this).parent().siblings('label').each(function(index){
                $(this).find('input').prop('checked', false);
            });
        }
    });

    $('.referenced-card').mouseover(function(event){
       $(this).find('img').addClass('show-hover');
    });

    $('.referenced-card').mouseout(function(event){
        $(this).find('img').removeClass('show-hover');
    });

    $('form').on('submit', function(event){
        event.preventDefault();
        let formData = new FormData(this);
        let params = new URLSearchParams(formData);
        params.append('form_type', this.id);
        window.location.replace('/search/' + '?' + params.toString());
    })
});