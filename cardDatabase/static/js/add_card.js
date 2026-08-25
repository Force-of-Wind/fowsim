let cards = [];
let currentIds = [];

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

function handleImagePreview(evt) {
    let fl_files = evt.target.files;
    let fl_file = fl_files[0];

    $('#importCardPreview').prop('src', URL.createObjectURL(fl_file));
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
    missingCards = [];
    try{
        json.fow.clusters.forEach(cluster => {
            cluster.sets.forEach(set => {
                set.cards.forEach(card => {
                    cards[card.id] = card;
                    if (card.wind_new)
                        newCards[card.id] = card.id;
                    if (currentIds.includes(card.id))
                        missingCards[card.id] = card.id;
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
        

    buildSelect(Object.keys(cards), newCards, missingCards);
}

function buildSelect(cardIds, newCards, missingCards){
    $('#importCardSelect').empty();
    $('#importCardSelect').append(`<option selected disabled>---</option>`);
    
    let options = cardIds.forEach(cardId => {
        let clss = newCards[cardId] ? 'new-card' : 'old-card';
        let clss2 = missingCards[cardId] ? 'existing-card' : 'missing-card';
        let hideOldCards = $('#onlyNewCards').is(':checked');
            
        $('#importCardSelect').append(`<option class="${clss} ${clss2}" value="${cardId}">${cardId}</option>`);
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

// Abilities can contain blank lines (e.g. nothing below the [Solo Mode] marker) or
// null entries, which would otherwise be saved as empty ability rows.
function cleanAbilities(abilities){
    if (!Array.isArray(abilities))
        return [];
    return abilities
        .filter(ability => ability !== null && ability !== undefined)
        .map(ability => String(ability).trim())
        .filter(ability => ability.length > 0);
}

// Split a card's abilities into the normal abilities and the Solo Mode abilities.
// The [Solo Mode] marker and everything after it belongs to Solo Mode; the marker
// itself is dropped since the dedicated textbox already implies the style.
function splitSoloModeAbilities(abilities){
    const marker = '[Solo Mode]';
    let cleaned = cleanAbilities(abilities);
    for (let i = 0; i < cleaned.length; i++){
        if (cleaned[i].includes(marker)){
            let solo = cleaned.slice(i + 1);
            let remainder = cleaned[i].replace(marker, '').trim();
            if (remainder)
                solo.unshift(remainder);
            return { normal: cleaned.slice(0, i), solo: solo };
        }
    }
    return { normal: cleaned, solo: [] };
}

function formatArtists(string, seperator = ' / '){
    return string.replaceAll(seperator, '\n');
}

function autofillFields(cardId){
    let card = cards[cardId];

    if(!card)
        return;

    changeValueOfInput('#add_card input[name="name"]', card.name);
    changeValueOfInput('#add_card input[name="card_id"]', card.id);
    changeValueOfInput('#add_card input[name="cost"]', card.cost);
    changeValueOfInput('#add_card input[name="divinity"]', card.divinity);
    changeValueOfInput('#add_card input[name="will_power"]', card.willpower);
    changeValueOfInput('#add_card textarea[name="flavour"]', card.flavour);
    changeValueOfInput('#add_card select[name="rarity"]', card.rarity);
    changeValueOfInput('#add_card input[name="ATK"]', card.ATK ?? "");
    changeValueOfInput('#add_card input[name="DEF"]', card.DEF ?? "");
    changeValueOfInput('#add_card textarea[name="artists"]', card.artist ? formatArtists(card.artist) : "");

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

    let splitAbilities = splitSoloModeAbilities(card.abilities ?? []);
    changeValueOfInput('#add_card textarea[name="ability_texts"]', arrayToText(splitAbilities.normal, '\r\n\r\n'));
    changeValueOfInput('#add_card textarea[name="solo_mode_ability_texts"]', arrayToText(splitAbilities.solo, '\r\n\r\n'));
}


$( document ).ready(function() {
    $('#upload').on('change', handleFileSelect);
    $('#id__card_image').on('change', handleImagePreview);
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
    $('#onlyMissingCards').change(function() {
        if(this.checked) {
            $('#importCardSelect').removeClass('all-loaded-cards');
            $('#importCardSelect').addClass('missing-cards-only');
        }
        else {
            $('#importCardSelect').removeClass('missing-cards-only');
            $('#importCardSelect').addClass('all-loaded-cards');
        }
    });
    currentIds = JSON.parse(document.getElementById('added_ids').textContent);
    let cachedJson = getCachedJson();
    if (cachedJson)
        collectCards(cachedJson);
});

onpageshow = (event) => {
    if ($('#onlyNewCards').is(':checked') == false) {
        $('#importCardSelect').removeClass('new-cards-only');
        $('#importCardSelect').addClass('all-cards');
    }
    if ($('#onlyMissingCards').is(':checked') == false) {
        $('#importCardSelect').removeClass('missing-cards-only');
        $('#importCardSelect').addClass('all-loaded-cards');
    }
};