$(function() {
    let LAST_DATABASE_URL = '';
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
        let decklist_data = {
            "zones": [],
            "name": $('.decklist-name').html().trim()
        };
        let zones = $('.deck-zone');
        for (let i = 0; i < zones.length; i++){
            let zone = zones.eq(i);
            let zone_data = {};
            zone_data.name = zone.find('.deck-zone-title').html().trim();
            zone_data.cards = [];
            let zone_cards = zone.find('.deck-zone-card');
            for (let j = 0; j < zone_cards.length; j++){
                let card = zone_cards.eq(j);
                let card_data = {};
                card_data.quantity = card.find('.card-quantity-input').val();
                card_data.id = card.data('card-id');
                card_data.position = j + 1;
                zone_data.cards.push(card_data);
            }
            decklist_data.zones.push(zone_data);
        }
        $.ajaxSetup({
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        });
        $.ajax({
            type: 'POST',
            url: `/save_decklist/${window.location.pathname.split('/')[2]}/`,
            data: JSON.stringify({
                decklist_data: decklist_data,
            }),
            success: function(data){
                console.log('Success');
            },
            error: function(data){
                console.log('Error');
            },
            contentType: 'application/json',
            dataType: 'json'
        })
    });

    $('.deck-zone-card').mouseover(function(event){
        $(this).find('img').addClass('show-hover');
    });

    $('.deck-zone-card').mouseout(function(event){
        $(this).find('img').removeClass('show-hover');
    });

    function getCookie(c_name)
    {
        // https://stackoverflow.com/questions/6506897/csrf-token-missing-or-incorrect-while-post-parameter-via-ajax-in-django
        if (document.cookie.length > 0)
        {
            c_start = document.cookie.indexOf(c_name + "=");
            if (c_start != -1)
            {
                c_start = c_start + c_name.length + 1;
                c_end = document.cookie.indexOf(";", c_start);
                if (c_end == -1) c_end = document.cookie.length;
                return unescape(document.cookie.substring(c_start,c_end));
            }
        }
        return "";
    }

    function setupOtherPages(){
        $('#other-pages a').each(function(index){
            $(this).on('click', function(event) {
                let page_num = $(this).data('page-index');
                if (page_num) {
                    let search_url = new URL(LAST_DATABASE_URL);
                    search_url.searchParams.set('page', page_num);
                    requestAndSetDatabaseContent(search_url.toString());
                }
            });
        });
    }

    function handleSubmit(event){
        event.preventDefault();
        let params = form_to_url_params(this);
        let search_url = window.location.origin + '/search/' + '?' + params.toString();
        requestAndSetDatabaseContent(search_url)
    }
    $('#advanced-form, #basic-form').on('submit', handleSubmit);

    function requestAndSetDatabaseContent(search_url){
        $.ajax({
            url: search_url,
            type: 'GET',
            dataType: 'html',
            success: function(data){
                LAST_DATABASE_URL = search_url;
                let result = $('<div />').append(data).find('#base-body').html();
                $('#database-container').html(result);
                initDatabaseBase();
                setupOtherPages();
                $('#advanced-form, #basic-form').on('submit', handleSubmit)
            }
        })
    }
});