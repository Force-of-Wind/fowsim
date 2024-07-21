$(function () {
    $('.decktype-select .mdb-select').materialSelect({
        'visibleOptions': 14,
        'placeholder': 'Search Format(s)...',
        'maxSelectedOptions': 1
    });

    $('.select-text-exactness input').change(function(){
        //Act like radio buttons, uncheck all the other ones in this form field
        if (this.checked){
            $(this).parent().siblings('label').each(function(index){
                $(this).find('input').prop('checked', false);
            });
        }
    });
});