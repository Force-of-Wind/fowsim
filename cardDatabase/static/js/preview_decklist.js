function togglePreviewDecklist(){
    if($('#database-container').hasClass('hidden-display')){
        $('#preview-decklist-container').addClass('hidden-display');
        $('#database-container').removeClass('hidden-display');
    }
    else if ($('#preview-decklist-container').hasClass('hidden-display')){
        refreshPreview();

        $('#preview-decklist-container').removeClass('hidden-display');
        $('#database-container').addClass('hidden-display');
    }    
}

function refreshPreview() 
{  
    //reset earlier data
    $('#image-container').empty();
    $('#image-container').append(generateZoneAndCardHtml());
}

function generateZoneAndCardHtml(){
    return getCardsAndZones().zones.reduce((generatedZoneHtml, zone) => {
        return generatedZoneHtml + `
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
    }, '');
}

function getDeckCount(cards) 
{
    return cards.reduce((count, card) => {
        return count + Number(card.quantity)
    }, 0);
}

function generateCardsHtml(cards) 
{
    return cards.reduce((generatedCardsHtml, currentCard)  =>{
        return generatedCardsHtml + `
            <div class="preview-deck-card">
                    <img class="preview-deck-card-img" src="${currentCard.imgUrl}" title="${currentCard.name}">
                    ${getHoverCardHtml(currentCard.imgUrls)}
                </div>
            `.repeat(currentCard.quantity);
    }, '');
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
    if($('#preview-decklist').length)
        $('#preview-decklist').click(togglePreviewDecklist);

    if($('#dialog-close').length)
        $('#dialog-close').click(togglePreviewDecklist);

    const refreshBc = new BroadcastChannel("refresh_channel");
    refreshBc.onmessage = () => {
        refreshPreview();
    };
});

