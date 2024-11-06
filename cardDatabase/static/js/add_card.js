let cards = [];

function handleFileSelect(evt) {
    let fl_files = evt.target.files;
    let fl_file = fl_files[0];

    if(fl_file){
        let reader = new FileReader();

        let display_file = (e) => {
            if(e.target.result){
                let json = JSON.parse(e.target.result)
                collectCards(json);
            }
        };

        let on_reader_load = (fl) => {
            return display_file;
        };
        
        reader.onload = on_reader_load(fl_file);
        
        reader.readAsText(fl_file);
    }
}

function cacheJson(json) {
    localStorage.setItem("cardsJson", JSON.stringify(json));
}

function getCachedJson() {
    let json = localStorage.getItem("cardsJson") ?? false;
    if (json)
        return JSON.parse(json);
}

function collectCards(json) {
    cacheJson(json);
    cards = [];
    newCards = [];
    try{
        json.fow.clusters.forEach(cluster => {
            cluster.sets.forEach(set => {
                set.cards.forEach(card => {
                    cards[card.id] = card;
                    if (card.wind_new)
                        newCards[card.id] = card.id;
                })
            });
        });
    }
    catch(error){
        console.error("Error while reading JSON");
        console.error(error);
    }

    if(Object.keys(cards) < 1){
        $('#importCardSelect').empty();
        $('#importCardSelect').addClass('hidden');
        return;
    }
        

    buildSelect(Object.keys(cards), newCards);
}

function buildSelect(cardIds, newCards){
    $('#importCardSelect').empty();
    $('#importCardSelect').append(`<option selected disabled>---</option>`);
    
    let options = cardIds.forEach(cardId => {
        let clss = newCards[cardId] ? 'new-card' : 'old-card';
        let hideOldCards = $('#onlyNewCards').is(':checked');
            
        $('#importCardSelect').append(`<option class="${clss}" value="${cardId}">${cardId}</option>`);
    });

    $('#importCardSelect').off('change');

    $('#importCardSelect').on('change', function(){
        autofillFields($(this).val());
    });

    if($('#importCardSelect').hasClass('hidden')){
        $('#importCardSelect').removeClass('hidden');
    }
}

function changeValueOfInput(query, value){
    $(`${query}`).val(value);
}

function mapFullTextColorToShortCode(fullTextColor){
    switch (fullTextColor) {
        case 'Light':
            return 'W';
        case 'Fire':
            return 'R';
        case 'Wind':
            return 'G';            
        case 'Water':
            return 'U';
        case 'Darkness':
            return 'B';
        case 'Void':
            return 'V';
        default:
            return '-';
    }
}

function arrayToText(array, seperator){
    return array.join(seperator);
}

function autofillFields(cardId){
    let card = cards[cardId];

    if(!card)
        return;

    changeValueOfInput('#add_card input[name="name"]', card.name);
    changeValueOfInput('#add_card input[name="card_id"]', card.id);
    changeValueOfInput('#add_card input[name="cost"]', card.cost);
    changeValueOfInput('#add_card input[name="divinity"]', card.divinity);
    changeValueOfInput('#add_card textarea[name="flavour"]', card.flavour);
    changeValueOfInput('#add_card select[name="rarity"]', card.rarity);
    changeValueOfInput('#add_card input[name="ATK"]', card.ATK ?? "");
    changeValueOfInput('#add_card input[name="DEF"]', card.DEF ?? "");

    //itterate to reset non chosen options
    $('#id_types input[type="checkbox"]').each((_, checkbox) => {
        let labelText = $($(checkbox).closest('label')[0]).text();
        labelText = labelText.replace('\n ', '').trim();
        $(checkbox).prop('checked', card.type.includes(labelText));
    });
    
    $('#id_colours input[type="checkbox"]').each((_, checkbox) => {
        let labelText = $($(checkbox).closest('label')[0]).text();
        labelText = labelText.replace('\n ', '').trim();
        let mappedCheckboxText = mapFullTextColorToShortCode(labelText);
        $(checkbox).prop('checked', card.colour.includes(mappedCheckboxText));
    });

    changeValueOfInput('#add_card textarea[name="races"]', arrayToText(card.race, '\r\n'));

    changeValueOfInput('#add_card textarea[name="ability_texts"]', arrayToText(card.abilities, '\r\n\r\n'));
}


$( document ).ready(function() {
    $('#upload').on('change', handleFileSelect);
    $('#onlyNewCards').change(function() {
        if(this.checked) {
            $('#importCardSelect').removeClass('all-cards');
            $('#importCardSelect').addClass('new-cards-only');
        }
        else {
            $('#importCardSelect').removeClass('new-cards-only');
            $('#importCardSelect').addClass('all-cards');
        }
    });
    let cachedJson = getCachedJson();
    if (cachedJson)
        collectCards(cachedJson);
});