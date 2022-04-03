$(function () {
    let LAST_DATABASE_URL = '';
    function setupCardClickables(){
        // Remove duplicate listeners when it gets called multiple times while generating new card html
        $('.card-quantity-plus').unbind('click');
        $('.card-quantity-minus').unbind('click');

        $('.card-quantity-minus').click(function(event){
            $(this).siblings('input').val(function(i, oldVal){
                return Math.max(parseInt(oldVal, 10) - 1, 1);
            });
            setZoneCount($(this).parents('.deck-zone').eq(0));
        });
        $('.card-quantity-plus').click(function(event){
            $(this).siblings('input').val(function(i, oldVal){
                return parseInt(oldVal, 10) + 1;
            });
            setZoneCount($(this).parents('.deck-zone').eq(0));
        });
        $('.deck-zone-cards .remove-card').on('click', function(event){
            let parent_deck_zone = $(this).parents('.deck-zone'); //Determine it before removing the element or jquery fails
            $(this).closest('.deck-zone-card').remove();
            setZoneCount(parent_deck_zone);
        });
        $('.remove-zone span').unbind('click');
        $('.remove-zone span').click(function(event){
            if(confirm(`Are you sure you want to delete the zone: ${$(this).siblings('.deck-zone-title').text().trim()}`)){
                $(this).parents('.deck-zone').remove();
            }
        });
        $('.deck-zone-title').unbind('blur keyup paste copy cut delete mouseup');
    }
    setupCardClickables();

    function setZoneCount(el){
        let zone_count = 0;
        $(el).find('.card-quantity').each(function(count_index){
            zone_count += parseInt($(this).find('input').val());
        });
        $(el).find('.zone-count').html(`[${zone_count}]`);
    }

    // Decklist sidebar logic
    function openDecklist() {
        $('.decklist-side-bar').css('width', '100%');
    }

    function closeDecklist() {
        $('.decklist-side-bar').css('width', '0');
    }

    // Set listeners on events
    $('.decklist-side-bar .closebtn')
        .on('click', function (event) {
            closeDecklist();
    });

    $('.openDecklistButton')
        .on('click', function (event) {
            openDecklist();
    });

    // Do it again for the add card sidebar
    function openAddSideBar() {
        $('.add-card-side-bar').css('width', '100%');
    }

    function closeAddSideBar() {
        $('.add-card-side-bar').css('width', '0');
    }

    // Set listeners on events
    $('.add-card-side-bar .closebtn')
        .on('click', function (event) {
            closeAddSideBar();
    });

    // Add card stuff
    function setupCardClicking() {
        $('.overlay-container').remove();
        $('#search-results .card img').each(function(index){
            $(this).parent()
                .removeAttr('href')
                .on('click', function(event){
                    event.preventDefault();
                    let card_name = $(this).closest('.card').data('card-name');
                    let card_id = $(this).closest('.card').data('card_id');
                    displayAddCardSidebar(card_name, card_id);
                })
        });
    }

    function displayAddCardSidebar(card_name, card_id) {
        $('#add-card-container')
            .empty()
            .append(`<div class="add-card-title">${card_name}</div>`)
            .append(getAddZoneHTML());

        $('.add-card-button').each(function(index){
            $(this).on('click', function (event) {       
                let zone_name = $(this).data('zone-name');
                let deck_zone = $(`.deck-zone .deck-zone-title:contains('${zone_name}')`).parent().parent();
                let deck_zone_cards = deck_zone.find('.deck-zone-cards');
                let card_matches = deck_zone_cards.find(`.deck-zone-card`).filter(function(){
                    return $(this).find('.deck-zone-card-name').text() === card_name;
                });
                if (!card_matches.length) {
                    let deck_card_html = createCardHtml(card_name, card_id);
                    deck_zone.find('.deck-zone-cards').append(deck_card_html);
                    setupCardClickables();
                } else {
                    // Already exists, just increment the value
                    let input_el = card_matches.find('.card-quantity input');
                    input_el.val(parseInt(input_el.val()) + 1);
                }
                setZoneCount(deck_zone);
            });
        });

        openAddSideBar();
    }

    // Gets all the zones and makes some buttons out of them
    function getAddZoneHTML(){
        let zones_titles = $('.deck-zone-title');

        let output = `<div class="add-to-zone-container"><div class="add-to-zone-container">`;
        zones_titles.each(function(index){
            let zone_name = $(this).html().trim();
            output += `<div class="add-card-button" data-zone-name="${zone_name}"><div class="add-card-button-title">Add to <b>${zone_name}</b></div></div>`;
        });
        output += `</div></div>`;
        return output;
    }

    function createCardHtml(name, img_url, card_id){
        return `<div class="deck-zone-card" data-card-id="${card_id}" draggable="true">
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

    // Database stuff copied from the other one
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
                setupCardClicking();
                $('#advanced-form, #basic-form').on('submit', handleSubmit)
            }
        })
    }
});