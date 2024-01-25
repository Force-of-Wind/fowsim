let zonesToLoadCards;
let availableZones;
let originalCards;
const startingHandSize = 5;

function initTestHandModule(cards, zones, buttonSelector, cardContainerSelector, drawButtonSelector, resetHandButtonSelector, zonePickerButton, zonePickerSelect, toggledZones) {
    availableZones = zones;
    originalCards = cards;
    zonesToLoadCards = toggledZones.map((zone) => { return zone.toLowerCase(); });

    zones.forEach((zone) => {
        if (zonesToLoadCards.includes(zone.toLowerCase()))
            $(zonePickerSelect).append(`<option selected value="${zone}">${zone}</option>`);
        else
            $(zonePickerSelect).append(`<option value="${zone}">${zone}</option>`);
    });

    setTestHandModule(cards, zones, buttonSelector, cardContainerSelector, drawButtonSelector, resetHandButtonSelector);

    $(zonePickerButton).off('click');
    $(zonePickerButton).on('click', function (e) {
        zonesToLoadCards = $(zonePickerSelect).val().map((zone) => { return zone.toLowerCase(); });
        setTestHandModule(originalCards, availableZones, buttonSelector, cardContainerSelector, drawButtonSelector, resetHandButtonSelector);
    });
}

function setTestHandModule(cards, zones, buttonSelector, cardContainerSelector, drawButtonSelector, resetHandButtonSelector) {
    let cardsForSelectedZones = cards.filter((card) => { return zonesToLoadCards.includes(card.zone.toLowerCase()) });

    let cardsToUse = buildCardWrappers(cardsForSelectedZones);

    $(cardContainerSelector).empty();
    //we need index
    cardsToUse = randomizeCards(cardsToUse);

    let startHand = cardsToUse.slice(0, startingHandSize)
    cardsToUse = cardsToUse.slice(startingHandSize, cardsToUse.length)
    startHand.forEach((card, index) => {
        $(cardContainerSelector).append(createHtmlForCard(card, index));
    });
    $(cardContainerSelector).css('--child-count', startingHandSize);

    $(drawButtonSelector).off('click');
    $(resetHandButtonSelector).off('click');

    $(drawButtonSelector).on('click', function (e) {
        let childCount = $(cardContainerSelector).children().length;
        if (cardsToUse[0]) {
            $(cardContainerSelector).append(createHtmlForCard(cardsToUse[0], childCount));
            cardsToUse = cardsToUse.slice(1, cardsToUse.length - 1)
            $(cardContainerSelector).css('--child-count', childCount + 1);
        }
    });

    $(resetHandButtonSelector).on('click', function (e) {
        setTestHandModule(originalCards, availableZones, buttonSelector, cardContainerSelector, drawButtonSelector, resetHandButtonSelector);
    });
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

function createHtmlForCard(card, childCount) {
    return `
        <img class="samplehand-card" src="${card.img}" style="--child-index:${childCount}; z-index:${childCount}">
    `
}