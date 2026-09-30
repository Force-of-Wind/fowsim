let zonesToLoadCards;
let availableZones;
let originalCards;
const startingHandSize = 5;

function initTestHandModule(cards, zones, buttonSelector, cardContainerSelector, drawButtonSelector, resetHandButtonSelector, mulliganButtonSelector, zonePickerButton, zonePickerSelect, toggledZones) {
    availableZones = zones;
    originalCards = cards;
    zonesToLoadCards = toggledZones.map((zone) => { return zone.toLowerCase(); });

    zones.forEach((zone) => {
        if (zonesToLoadCards.includes(zone.toLowerCase()))
            $(zonePickerSelect).append(`<option selected value="${zone}">${zone}</option>`);
        else
            $(zonePickerSelect).append(`<option value="${zone}">${zone}</option>`);
    });

    setTestHandModule(cards, zones, buttonSelector, cardContainerSelector, drawButtonSelector, resetHandButtonSelector, mulliganButtonSelector);

    $(zonePickerButton).off('click');
    $(zonePickerButton).on('click', function (e) {
        zonesToLoadCards = $(zonePickerSelect).val().map((zone) => { return zone.toLowerCase(); });
        setTestHandModule(originalCards, availableZones, buttonSelector, cardContainerSelector, drawButtonSelector, resetHandButtonSelector, mulliganButtonSelector);
    });
}

function setTestHandModule(cards, zones, buttonSelector, cardContainerSelector, drawButtonSelector, resetHandButtonSelector, mulliganButtonSelector) {
    let cardsForSelectedZones = cards.filter((card) => { return zonesToLoadCards.includes(card.zone.toLowerCase()) });

    // The deck holds every card not currently in hand; the hand is what is shown to the player.
    let deck = randomizeCards(buildCardWrappers(cardsForSelectedZones));
    let hand = deck.splice(0, startingHandSize);

    renderHand(hand, cardContainerSelector, 0);

    $(drawButtonSelector).off('click');
    $(resetHandButtonSelector).off('click');
    $(mulliganButtonSelector).off('click');

    $(drawButtonSelector).on('click', function (e) {
        if (deck.length) {
            hand.push(deck.shift());
            // Only animate the freshly drawn card, leave the rest in place.
            renderHand(hand, cardContainerSelector, hand.length - 1);
        }
    });

    $(mulliganButtonSelector).on('click', function (e) {
        const selectedIndices = getSelectedCardIndices(cardContainerSelector);
        if (selectedIndices.length === 0) {
            return;
        }

        // Pull the selected cards out of the hand (highest index first so splicing stays valid).
        selectedIndices.sort((a, b) => b - a).forEach((index) => {
            deck.push(hand[index]);
            hand.splice(index, 1);
        });

        // Shuffle them back in, then draw the same number of fresh cards.
        deck = randomizeCards(deck);
        const drawCount = Math.min(selectedIndices.length, deck.length);
        hand.push(...deck.splice(0, drawCount));

        // The whole hand is reshuffled, so re-deal every card.
        renderHand(hand, cardContainerSelector, 0);
    });

    $(resetHandButtonSelector).on('click', function (e) {
        setTestHandModule(originalCards, availableZones, buttonSelector, cardContainerSelector, drawButtonSelector, resetHandButtonSelector, mulliganButtonSelector);
    });
}

// animateStartIndex: cards at this index and after deal in from the left, staggered.
// Cards before it appear instantly (they were already on the table).
function renderHand(hand, cardContainerSelector, animateStartIndex = 0) {
    const staggerMs = 90;
    $(cardContainerSelector).empty();
    hand.forEach((card, index) => {
        const animDelay = index >= animateStartIndex ? (index - animateStartIndex) * staggerMs : null;
        $(cardContainerSelector).append(createHtmlForCard(card, index, animDelay));
    });
    $(cardContainerSelector).css('--child-count', hand.length);
}

function getSelectedCardIndices(cardContainerSelector) {
    let selectedIndices = [];
    $(cardContainerSelector).find('.samplehand-card-wrapper').each(function (index) {
        if ($(this).find('.samplehand-card-checkbox').is(':checked')) {
            selectedIndices.push(index);
        }
    });
    return selectedIndices;
}

function randomizeCards(array) {
    let randomizeIterations = 3;
    for (let i = 0; i < randomizeIterations; i++) {
        array = fisherYatesShuffle(array);
    }

    return array;
}

function fisherYatesShuffle(array) {
    for (let i = array.length - 1; i >= 0; i--) {
        const randomIndex = Math.floor(Math.random() * (i + 1));
        array.push(array[randomIndex]);
        array.splice(randomIndex, 1);
    }
    return array;
}

function buildCardWrappers(cards) {
    let mappedCards = [];

    cards.forEach((card) => {
        for (let i = 0; i < card.quantity; i++) {
            mappedCards.push(card);
        }
    });

    return mappedCards;
}

function createHtmlForCard(card, childCount, animDelay = null) {
    const dealing = animDelay !== null;
    const dealingClass = dealing ? ' dealing' : '';
    const animStyle = dealing ? ` animation-delay:${animDelay}ms;` : '';
    return `
        <div class="samplehand-card-wrapper${dealingClass}" style="--child-index:${childCount}; z-index:${childCount};${animStyle}">
            <input type="checkbox" class="samplehand-card-checkbox" title="Select for mulligan" aria-label="Select card for mulligan">
            <img class="samplehand-card" src="${card.img}">
        </div>
    `
}
