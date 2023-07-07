$(function() {
    let LAST_DATABASE_URL = '';
    function setupCardClickables(){
        // Remove duplicate listeners when it gets called multiple times while generating new card html       
        const refreshBc = new BroadcastChannel("refresh_channel");
        $('.card-quantity-plus').unbind('click');
        $('.card-quantity-minus').unbind('click');

        $('.card-quantity-minus').click(function(event){
            $(this).siblings('input').val(function(i, oldVal){
                return Math.max(parseInt(oldVal, 10) - 1, 1);
            });
            setZoneCount($(this).parents('.deck-zone').eq(0));
            refreshBc.postMessage('refresh');
        });
        $('.card-quantity-plus').click(function(event){
            $(this).siblings('input').val(function(i, oldVal){
                return parseInt(oldVal, 10) + 1;
            });
            setZoneCount($(this).parents('.deck-zone').eq(0));
            refreshBc.postMessage('refresh');
        });
        $('.deck-zone-cards .remove-card').on('click', function(event){
            let parent_deck_zone = $(this).parents('.deck-zone'); //Determine it before removing the element or jquery fails
            $(this).closest('.deck-zone-card').remove();
            setZoneCount(parent_deck_zone);
            refreshBc.postMessage('refresh');
        });
        
        $(".card-quantity-input").change(() => {refreshBc.postMessage('refresh')});
        $('.remove-zone span').unbind('click');
        $('.remove-zone span').click(function(event){
            let el_title = $(this).parent().siblings('.deck-zone-title').text().trim();
            if(confirm(`Are you sure you want to delete the zone: ${el_title}`)) {
                if (FOWDB_IS_MOBILE) {
                    $('#zone-counts .zone-count-title').each(function (index) {
                        if ($(this).html().trim() == el_title) {
                            $(this).next().remove();
                            $(this).remove();                            
                            return false;
                        }
                    });
                }
                $(this).parents('.deck-zone').remove();
                if (!FOWDB_IS_MOBILE) {
                    setupCardOverlay();
                }
                refreshBc.postMessage('refresh');
            }
        });

        if (FOWDB_IS_MOBILE) {
            $('.deck-zone-title').on('focusin', function () {
                $(this).data('prev-val', $(this).html().trim());
                refreshBc.postMessage('refresh');
            });
        }
        $('.decklist-name').off('paste').on('paste', () => {handlePaste; refreshBc.postMessage('refresh');});
        $('.deck-zone-title').unbind('blur keyup paste copy cut delete mouseup');
        $('.deck-zone-title').on('blur keyup paste copy cut delete mouseup', function (event) {
            if (event.type == 'paste'){
                handlePaste(event);
                refreshBc.postMessage('refresh');
            }
            if (FOWDB_IS_MOBILE){
                let prev_val = $(this).data('prev-val');
                let that = this;
                $('.zone-count-title').each(function(index){
                    if ($(this).html().trim() == prev_val){
                        $(this).html($(that).html().trim());
                        $(that).data('prev-val', $(that).html().trim());
                        refreshBc.postMessage('refresh');
                        return false;
                    }
                });
            } else {
                setupCardOverlay();
                refreshBc.postMessage('refresh');
            }
        });


        function openCardInNewTab(card_url){
            window.open(card_url, '_blank').focus();
        }

        $('.deck-zone-card-name').off('mousedown').on('mousedown', function(event){
            // Prevent auto scroller from appearing when middle clicking
            if (event.which == 2) event.preventDefault();
        });

        $('.deck-zone-card-name').off('click auxclick').on('click auxclick', function(event){
            openCardInNewTab(FOWDB_VIEW_CARD_URL + $(this).parents('.deck-zone-card').data('card-id'));
        });

    }
    setupCardClickables();
    function setZoneCount(el){
        let zone_count = 0;
        let zone_name = $(el).find('.deck-zone-title').html().trim();
        $(el).find('.card-quantity').each(function(count_index){
            zone_count += parseInt($(this).find('input').val());
        });
        $(el).find('.zone-count').html(`[${zone_count}]`);
        if (FOWDB_IS_MOBILE){
            $('#zone-counts .zone-count-title').each(function(index){
                if ($(this).html().trim() == zone_name ){
                    $(this).next().html(zone_count);
                }
            });
        }
    }

   function handlePaste(event){
       event.preventDefault();
       let paste = window.event.clipboardData.getData('text');
       document.execCommand("insertHTML", false, paste);
   }

    $('.deck-zone').each(function (index) {
        setZoneCount(this)
    });
    function saveDeck(event){
        $('#save-deck-button').off('click');  // Stop double clicks from sending multiple save requests and messing up data
        let decklist_data = {
            "zones": [],
            "name": $('.decklist-name').html().trim(),
            "comments": $('#comments').val()
        };
        let zones = $('.deck-zone');
        for (let i = 0; i < zones.length; i++) {
            let zone = zones.eq(i);
            let zone_data = {};
            zone_data.name = zone.find('.deck-zone-title').html().trim();
            zone_data.cards = [];
            let zone_cards = zone.find('.deck-zone-card');
            for (let j = 0; j < zone_cards.length; j++) {
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
                is_public: $('#public-input').is(":checked")
            }),
            success: function (data) {
                window.onbeforeunload = undefined; // Remove warning of unsaved changes
                window.location.assign(`/view_decklist/${data.decklist_pk}`);
            },
            error: function (data) {
                $('#save-deck-button').click(saveDeck);  // Reenable save button, something unexpected happened
                alertify.error('Error saving deck');
            },
            contentType: 'application/json',
        })
    }
    $('#save-deck-button').click(saveDeck);

    $('#new-zone-button').on('click', function (event) {
        let output = `<div class="deck-zone"><div class="deck-zone-title-container"><div class="zone-count">[0]</div><span class="deck-zone-title" contenteditable="true">New Zone</span><div class="remove-zone"><span>&#10006;</span></div></div><div class="deck-zone-cards"></div></div>`;
        $('.deck-zones-container').append(output);
        if(FOWDB_IS_MOBILE) {
            let counts_output = `<div class="zone-count-title">New Zone</div> <div class="zone-count-preview">0</div>`
            $('#zone-counts').append(counts_output)
        } else {
            // If any search results are showing, add the new zone to those cards
            setupCardOverlay();
            setupDraggableCards();
        }
        setupCardClickables();
        setupEditableContent();
    });

    function hoverCardMouseOver(event){
        $(this).find('img').addClass('show-hover');
        $(this).find('.multi-hovered-img').addClass('show-hover');
    }

    function hoverCardMouseOut(event){
        $(this).find('img').removeClass('show-hover');
        $(this).find('.multi-hovered-img').removeClass('show-hover');
    }

    if(!FOWDB_IS_MOBILE) {
        $('.deck-zone-card-name').mouseover(hoverCardMouseOver);

        $('.deck-zone-card-name').mouseout(hoverCardMouseOut);
    }

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
        $('.pagination a').each(function(index){
            $(this).on('click', function(event) {
                event.preventDefault();
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
                initSearch();
                initDatabaseBase();
                setupOtherPages();
                window.scrollTo(0,0); // Go back to the top now that the new page has been loaded
                if(FOWDB_IS_MOBILE){
                    setupCardClicking();
                } else {
                    setupCardOverlay();
                }
                $('#advanced-form, #basic-form').on('submit', handleSubmit)
            }
        })
    }

    function getHoverCardHtml(urls){
        let output = '';
        output += '<div class="multi-hovered-img">';
        urls.forEach(el => output += `<img class="hover-card-img" src="${el}"/>`);
        output += '</div>';
        return output;
    }

    function createCardHtml(name, img_urls, card_id){
        return `<div class="deck-zone-card" data-card-id="${card_id}" data-card-img-urls="${img_urls}" data-card-name="${name}" draggable="true">
                    <div class="card-quantity">
                        <a href="#" class="card-quantity-minus">
                            <span>-</span>
                        </a>
                        <input type="number" class="card-quantity-input" value="1">
                        <a href="#" class="card-quantity-plus">
                            <span>+</span>
                        </a>
                    </div>
                    <div class="deck-zone-card-name">${name}${getHoverCardHtml(img_urls)}</div>
                    <div class="remove-card">&#10006;</div>
                </div>`
    }

    function setupEditableContent(){
        $('span[contenteditable]').unbind('keydown');
        $('span[contenteditable]').keydown(function(e) {
            if (e.keyCode === 13) { //Enter key, do nothing
                return false;
            }
        });
    }
    if(!FOWDB_IS_MOBILE) {
        setupEditableContent();
    }

    function setupCardOverlay(){
        $('.overlay-container').remove();
        $('#search-results .card img').each(function(index){
            $(this).parent().append(getOverlayHTML($(this).parents('a').attr('href')));
        });
        $('.overlay-zone:not(.view-card-link)').on('click', function(event){
            event.preventDefault();
            let card_name = $(this).closest('.card').data('card-name');
            let zone_name = $(this).data('zone-name');
            let deck_zone = $(`.deck-zone .deck-zone-title:contains('${zone_name}')`).parent().parent();
            let card_id = $(this).closest('.card').data('card-id');
            let card_img_urls = $(this).closest('.card').data('card-image-urls');
            let deck_zone_cards = deck_zone.find('.deck-zone-cards');
            let card_matches = deck_zone_cards.find(`.deck-zone-card`).filter(function(){
                return $(this).find('.deck-zone-card-name').text() === card_name;
            });
            if (!card_matches.length) {
                let deck_card_html = createCardHtml(card_name, card_img_urls, card_id);
                deck_zone.find('.deck-zone-cards').append(deck_card_html);
                deck_zone.find('.deck-zone-card-name').mouseout(hoverCardMouseOut);
                deck_zone.find('.deck-zone-card-name').mouseover(hoverCardMouseOver);
                setupCardClickables();
                setupDraggableCards();
            } else {
                // Already exists, just increment the value
                let input_el = card_matches.find('.card-quantity input');
                input_el.val(parseInt(input_el.val()) + 1);
            }
            setZoneCount(deck_zone);
        });
    }

    function getOverlayHTML(card_href){

        let zones_titles = $('.deck-zone-title');

        let output = `<div class="overlay-container"><div class="card-overlay">`;
        zones_titles.each(function(index){
            let zone_name = $(this).html().trim();
            output += `<div class="overlay-zone" data-zone-name="${zone_name}"><div class="overlay-zone-title">Add to <b>${zone_name}</b></div></div>`;
        });

        output += `<div class="overlay-zone view-card-link"><a href="${card_href}" target="_blank"><div class="overlay-zone-title">Go to Card</div></a></div>`;

        output += `</div></div>`;
        return output;
    }

    function setupDraggableCards() {
        const refreshBc = new BroadcastChannel("refresh_channel");
        $('.deck-zone-card')
            .off('drag')
            .off('dragstart')
            .off('dragend')
            .on('drag', function (event) {

            })
            .on('dragstart', function (event) {
                // Fade out the dragged card and hide the popup so it doesn't appear
                // in the drag preview.
                $(this).find('img').removeClass('show-hover');
                event.target.style.opacity = .5;
                event.originalEvent.dataTransfer.setDragImage(event.target, 0, 0);
                dragged = event.target;
            })
            .on('dragend', function (event) {
                event.target.style.opacity = 1;
                refreshBc.postMessage('refresh');
            });

        $('.deck-zone')
            .off('dragover')
            .off('drop')
            .on('dragover', false)
            .on('drop', function (event) {
                event.preventDefault();

                // Need to check if it was dropped on a card or just on a zone.
                // Using closest so we can drop it on anything and have it work - for example
                // if somebody drops it on the title of a zone we still want it to work.
                let droppedOnCard = $(event.target).closest('.deck-zone-card');
                let droppedOnZone = $(event.target).closest('.deck-zone');
                let deckZoneCards = $(droppedOnZone[0]).children('.deck-zone-cards')[0];

                let previousParent = $(dragged).parent().parent();
                dragged.style.opacity = 1;

                let insertIntoList;

                if (droppedOnCard.length > 0) {
                    insertIntoList = true;
                }
                else if (droppedOnZone.length > 0) {
                    insertIntoList = false;
                }
                else {
                    return;
                }

                let cardExists = false;
                // Check if the card already exists in the zone
                let cardMatches = $(deckZoneCards).find(`.deck-zone-card`).filter(function () {
                    return $(this).find('.deck-zone-card-name').text() === $(dragged).find('.deck-zone-card-name').text();
                });

                // The existing card logic only runs if it was not dropped on the same zone
                let droppedOnTheSameZone = previousParent[0] == droppedOnZone[0];
                cardExists = cardMatches.length > 0 && !droppedOnTheSameZone;

                // Holding shift duplicates the card instead of moving it
                if (event.shiftKey && !droppedOnTheSameZone) {
                    let clonedCard = dragged.cloneNode(true);

                    // If the card exists we need to increment the number of cards instead
                    // of adding a new element.
                    if (cardExists) {
                        let previousInputEl = $(dragged).find('.card-quantity input');
                        let input_el = cardMatches.find('.card-quantity input');
                        input_el.val(parseInt(input_el.val()) + parseInt(previousInputEl.val()));
                    }
                    // If a card is dropped directly onto a card in a list, we want to put it before
                    // that specific card to allow for reordering.
                    else if (insertIntoList) {
                        droppedOnCard.before(clonedCard);
                    }
                    // Otherwise, put it at the end of the list as normal.
                    else {
                        deckZoneCards.appendChild(clonedCard);
                    }

                    $(clonedCard).find('.deck-zone-card-name').mouseout(hoverCardMouseOut);
                    $(clonedCard).find('.deck-zone-card-name').mouseover(hoverCardMouseOver);
                }
                else {
                    if (cardExists) {
                        let previousInputEl = $(dragged).find('.card-quantity input');
                        let input_el = cardMatches.find('.card-quantity input');
                        input_el.val(parseInt(input_el.val()) + parseInt(previousInputEl.val()));
                        $(dragged).remove();
                    }
                    else if (insertIntoList) {
                        droppedOnCard.before(dragged);
                    }
                    else {
                        deckZoneCards.appendChild(dragged);
                    }
                }

                setupCardClickables();
                setupEditableContent();
                setupDraggableCards();
                setZoneCount(droppedOnZone[0]);
                setZoneCount(previousParent);

                refreshBc.postMessage('refresh');
            });
    }
    if(!FOWDB_IS_MOBILE) {
        setupDraggableCards();
    }

    // Decklist sidebar logic
    function openDecklist() {
        $('.decklist-side-bar').css({'width': '100%', 'right': '0'});
    }

    function closeDecklist() {
        $('.decklist-side-bar').css({'width': '0', 'right': '-5px'});
    }

    // Do it again for the add card sidebar
    function openAddSideBar() {
        $('.add-card-side-bar').css('width', '100%');
    }

    function closeAddSideBar() {
        $('.add-card-side-bar').css('width', '0');
    }

    if(FOWDB_IS_MOBILE) {
        // Set listeners on events
        $('.add-card-side-bar .closebtn')
            .on('click', function (event) {
                closeAddSideBar();
            });
        $('.decklist-side-bar .closebtn')
            .on('click', function (event) {
                closeDecklist();
            });

        $('.openDecklistButton')
            .on('click', function (event) {
                openDecklist();
            });
    }

    // Add card stuff
    function setupCardClicking() {
        $('.overlay-container').remove();
        $('#search-results .card img').each(function(index){
            $(this).parent()
                .removeAttr('href')
                .on('click', function(event){
                    event.preventDefault();
                    let card_name = $(this).closest('.card').data('card-name');
                    let card_id = $(this).closest('.card').data('card-id');
                    let card_img_urls = $(this).parent().data('card-image-urls');
                    displayAddCardSidebar(card_name, card_id, card_img_urls);
                })
        });
    }

    function displayAddCardSidebar(card_name, card_id, card_img_urls) {
        $('#add-card-container')
            .empty()
            .append(getCardTitleHTML(card_name))
            .append(getCardImgHTML(card_img_urls))
            .append(getAddZoneHTML());

        $('.add-card-button').each(function(index){
            $(this).on('click', function (event) {
                let quantity = 1;
                let zone_name = $(this).data('zone-name');
                let deck_zone = $(`.deck-zone .deck-zone-title:contains('${zone_name}')`).parent().parent();
                let deck_zone_cards = deck_zone.find('.deck-zone-cards');
                let card_matches = deck_zone_cards.find(`.deck-zone-card`).filter(function(){
                    return $(this).find('.deck-zone-card-name').text() === card_name;
                });
                if (!card_matches.length) {
                    let deck_card_html = createCardHtml(card_name, card_img_urls, card_id);
                    deck_zone.find('.deck-zone-cards').append(deck_card_html);
                    setupCardClickables();
                } else {
                    // Already exists, just increment the value
                    let input_el = card_matches.find('.card-quantity input');
                    input_el.val(parseInt(input_el.val()) + 1);
                    quantity = input_el.val();
                }
                setZoneCount(deck_zone);
                let quantity_modifier = getQuantityOrdinal(parseInt(quantity)); // 'st', 'nd', 'rd', 'th'
                alertify.success(`Added ${quantity}${quantity_modifier} ${card_name} to ${zone_name}`);
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

    function getCardImgHTML(url){
        return  `<div class="card-img-container"><img class="card-img" src="${url}" /></div>`
    }

    function getCardTitleHTML(name){
        return `<div class="add-card-title">${name}</div>`
    }

    function setupAlertify(){
        alertify.defaults.notifier.delay = 2;
        if (FOWDB_IS_MOBILE) {
            alertify.defaults.notifier.position = 'top-left';
        } else {
            alertify.defaults.notifier.position = 'bottom-left';
        }
    }

    setupAlertify();

    function getQuantityOrdinal(d){
        const dString = String(d);
        const last = +dString.slice(-2);
        if (last > 3 && last < 21) return 'th';
        switch (last % 10) {
            case 1:  return "st";
            case 2:  return "nd";
            case 3:  return "rd";
            default: return "th";
        }
    }

});

window.onbeforeunload = function (e) {
    return 'Are you sure? You may have unsaved changes.';
};