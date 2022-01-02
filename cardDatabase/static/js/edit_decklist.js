$(function() {
    let LAST_DATABASE_URL = '';
    function setupCardClickables(){
        // Remove duplicate listeners when it gets called multiple times while generating new card html
        $('.card-quantity-plus').unbind('click');
        $('.card-quantity-minus').unbind('click');

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
        $('.deck-zone-cards .remove-card').on('click', function(event){
            $(this).closest('.deck-zone-card').remove();
        });

        $('.deck-zone-title').on('blur keyup paste copy cut delete mouseup', function(event){
            setupCardOverlay();
        })
    }
    setupCardClickables();
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
        })
    });

    $('#new-zone-button').on('click', function(event){
        let output = `<div class="deck-zone"><div class="deck-zone-title" contenteditable="true">New Zone</div><div class="deck-zone-cards"></div></div>`;
        $('.deck-zones-container').append(output);
        // If any search results are showing, add the new zone to those cards
        setupCardOverlay();
        setupCardClickables();
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
                setupCardOverlay();
                $('#advanced-form, #basic-form').on('submit', handleSubmit)
            }
        })
    }

    function createCardHtml(name, img_url, card_id){
        return `<div class="deck-zone-card" data-card-id="${card_id}">
                    <div class="card-quantity">
                        <a href="#" class="card-quantity-minus">
                            <span>-</span>
                        </a>
                        <input type="text" class="card-quantity-input" value="1">
                        <a href="#" class="card-quantity-plus">
                            <span>+</span>
                        </a>
                    </div>
                    <div class="deck-zone-card-name">${name}<img class="hover-card-img" src="${img_url}"></div>
                    <div class="remove-card">&#10006;</div>
                </div>`
    }

    function setupCardOverlay(){
        $('.overlay-container').remove();
        $('#search-results .card img').each(function(index){
            $(this).parent().append(getOverlayHTML());
        });
        $('.overlay-zone').on('click', function(event){
            event.preventDefault();
            let card_name = $(this).closest('.card').data('card-name');
            let zone_name = $(this).data('zone-name');
            let deck_zone = $(`.deck-zone .deck-zone-title:contains('${zone_name}')`).parent();
            let card_id = $(this).closest('.card').data('card-id');
            let card_img_url = $(this).closest('.card').data('card-image-url');
            let deck_zone_cards = $(`.deck-zone .deck-zone-title:contains('${zone_name}')`).parent().find('.deck-zone-cards');
            let card_matches = deck_zone_cards.find(`.deck-zone-card:contains('${card_name}')`)
            if (!card_matches.length) {
                let deck_card_html = createCardHtml(card_name, card_img_url, card_id);
                deck_zone.find('.deck-zone-cards').append(deck_card_html);
                setupCardClickables();
            } else {
                // Already exists, just increment the value
                let input_el = card_matches.find('.card-quantity input');
                input_el.val(parseInt(input_el.val()) + 1);
            }
        });
    }

    function getOverlayHTML(){

        let zones_titles = $('.deck-zone-title');

        let output = `<div class="overlay-container"><div class="card-overlay">`;
        zones_titles.each(function(index){
            let zone_name = $(this).html().trim();
            output += `<div class="overlay-zone" data-zone-name="${zone_name}"><div class="overlay-zone-title">Add to <b>${zone_name}</b></div></div>`;
        });
        output += `</div></div>`;
        return output;
    }
});