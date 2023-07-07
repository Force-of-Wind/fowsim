function togglePreviewDecklist(){
    if($('#preview-decklist-container').hasClass('active-display')){
        $('#preview-decklist-container').removeClass('active-display');
        $('#preview-decklist-container').addClass('hidden-display');

        $('#decklist-css').prop('disabled', true);

        $('#database-container').removeClass('hidden-display');
        $('#database-container').addClass('active-display');
    }
    else if ($('#database-container').hasClass('active-display')){
        $('#image-container').empty(); //reset earlier data

        let html = generateZoneAndCardHtml();

        $('#image-container').append(html);

        $('#preview-decklist-container').removeClass('hidden-display');
        $('#preview-decklist-container').addClass('active-display');

        $('#database-container').removeClass('active-display');
        $('#database-container').addClass('hidden-display');
    }    
}

function refreshPreview() 
{  
    $('#image-container').empty(); //reset earlier data

    let html = generateZoneAndCardHtml();

    $('#image-container').append(html);
}

function generateZoneAndCardHtml(){
    let decklist_data = getCardsAndZones();

    let html = '';

    decklist_data.zones.map(zone => {
        html +=  `
        <div class="preview-deck-zone">
            <div class="preview-deck-zone-title">
                ${zone.name}
            </div>
            <div class="preview-deck-zone-count">[${getDeckCount(zone.cards)}]</div>
            <div class="preview-deck-zone-card-container">
                ${generateCardsHtml(zone.cards)}    
            </div>
        </div>
    `
    });

    return html;
}

function getDeckCount(cards) 
{  
    let count = 0;

    cards.forEach(card => {
        count += 1 * card.quantity
    });

    return count
}

function generateCardsHtml(cards) 
{
    let html = '';

    cards.forEach(card => {
        for (let index = 0; index < card.quantity; index++) {
            html += `
            <div class="preview-deck-card">
                    <img class="preview-deck-card-img" src="${card.imgUrl}" title="${card.name}">
                    ${getHoverCardHtml(card.imgUrls)}
                </div>
            `;
        }
    })

    return html;
}

function getCardsAndZones(){
    let zones = $('.deck-zone');
    let decklist_data = {
        zones: []
    };
    for (let i = 0; i < zones.length; i++) {
        let zone = zones.eq(i);
        let zone_data = {};
        zone_data.name = zone.find('.deck-zone-title').html().trim();
        zone_data.cards = [];
        let zone_cards = zone.find('.deck-zone-card');
        for (let j = 0; j < zone_cards.length; j++) {
            let card = zone_cards.eq(j);
            let card_data = {};
            let card_urls = card.data('card-img-urls').split(',');
            card_data.quantity = card.find('.card-quantity-input').val();
            card_data.id = card.data('card-id');
            //this is for double faced cards that are added via JS to only show the front side            
            card_data.imgUrls = card_urls;
            card_data.imgUrl = card_urls[0];
            card_data.name = card.data('card-name');
            card_data.position = j + 1;
            zone_data.cards.push(card_data);
        }
        decklist_data.zones.push(zone_data);
    }

    return decklist_data
}

function getHoverCardHtml(urls){
    let output = '';
    output += '<div class="multi-hovered-img">';
    urls.forEach(el => output += `<img class="hover-card-img" src="${el}"/>`);
    output += '</div>';
    return output;
}

$(document).ready(function () {
    $('#preview-decklist').click(togglePreviewDecklist);
    $('#refresh-preview').click(refreshPreview);
});

