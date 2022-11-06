function form_to_url_params(form){
    let formData = new FormData(form);
    let params = new URLSearchParams(formData);
    params.append('form_type', form.id);
    return params;
}

function initDatabaseBase(){
    function focusOnInit(el){
        if (!FOWDB_IS_MOBILE){
            el.focus()
        }
    }
    focusOnInit($('#basic-form input[type="text"]'));

    $('#advanced-search-toggle').on('click',
        function (event){
            $('#basic-search').hide();
            $('#advanced-search').show();
            $('#search-toggles').removeClass('basic-showing');
            $('#search-toggles').addClass('advanced-showing');
            focusOnInit($('#advanced-form input[name="generic_text"]'));
        });
    $('#basic-search-toggle').on('click',
        function(event){
            $('#basic-search').show();
            $('#advanced-search').hide();
            $('#search-toggles').addClass('basic-showing');
            $('#search-toggles').removeClass('advanced-showing');
            focusOnInit($('#basic-form input[name="generic_text"]'));
        });

    $('.race-select .mdb-select').materialSelect({
        'visibleOptions': 14,
        'placeholder': 'Search Race(s)...',
        'maxSelectedOptions': 2
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
    $('.keywords-select .mdb-select').materialSelect({
        'visibleOptions': 14,
        'placeholder': 'Search Keyword(s)...',
        'maxSelectedOptions': 2
    });

    $('.select-text-exactness input, .select-sort-by input, .colour-match input, .colour-combination input').change(function(){
        //Act like radio buttons, uncheck all the other ones in this form field
        if (this.checked){
            $(this).parent().siblings('label').each(function(index){
                $(this).find('input').prop('checked', false);
            });
        }
    });

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
    if (FOWDB_USE_DEFAULT_DATABASE_SUBMIT) {
        $('form').on('submit', function (event) {
            event.preventDefault();
            let formData = new FormData(this);
            for (let fieldName of ['atk_value', 'def_value']){
                if (!formData.get(fieldName)){
                    formData.delete(fieldName);
                    formData.delete(fieldName.substring(0, 4) + 'comparator');
                }
            }
            if (!formData.get('colours')){
                formData.delete('colour_match')
            }
            formData.append('generic_text', formData.get('generic_text').replace(/[\u2018\u2019]/g, "'")
                .replace(/[\u201C\u201D]/g, '"')); // Fix weird apostrophes
            let params = new URLSearchParams(formData);
            params.append('form_type', this.id);
            window.location.assign('/search/' + '?' + params.toString());
        });
    }

    function select_format_sets(format_clusters, set_active){
        for (let i = 0; i < format_clusters.length; i++){
            let cluster = format_clusters[i];
            for (let j = 0; j < cluster.sets.length; j++) {
                let format_set = cluster.sets[j];
                let set_mdb_select = $(`.sets-select .mdb-select ul span.filtrable:contains('${format_set.name.replace("'", "\\'")}')`);
                if (set_active && !set_mdb_select.parent().hasClass('active') ||
                    !set_active && set_mdb_select.parent().hasClass('active')){
                    set_mdb_select.click();
                }
            }
        }
    }
    $('#new-frontiers-select').click(function(event){
        event.preventDefault();
        let NF_clusters = FOWDB_SET_JSON.clusters.slice(FOWDB_SET_JSON.clusters.length - 2, FOWDB_SET_JSON.clusters.length);
        select_format_sets(NF_clusters, true);
    });
    $('#wanderer-select').click(function(event){
        event.preventDefault();
        //TODO Remove OG Valhalla if it gets added
        select_format_sets(FOWDB_SET_JSON.clusters, true);
    });
    $('#clear-all-sets').click(function(event){
        event.preventDefault();
        select_format_sets(FOWDB_SET_JSON.clusters, false);
    });
    $('.help-tooltip').on('click', function(event){
        if (event.target === this || event.target.matches('.tooltip-icon')) {
            $(this).addClass('show');
            $('.tooltip-popup').on('click', checkIfCloseTooltip);
            $(document).on('keyup', checkIfCloseTooltip);
        }
    });

    function checkIfCloseTooltip(event){
        if (event.target === event.currentTarget || event.key == 'Escape') {
            closeTooltip();
        }
    }
    function closeTooltip(){
        $('.help-tooltip.show').removeClass('show');
        $('.tooltip-popup').off('click', checkIfCloseTooltip);
    }
}
$(function(){
    initDatabaseBase();
});