function initTestHandModule(cards, buttonSelector, cardContainerSelector, drawButtonSelector) {

    let cardsToUse = buildCardWrappers(cards);

    let defaultToggledZones = ['Main', 'Main Deck'];

    const originalCardStack = [...cardsToUse];
    //cleanup
    $(cardContainerSelector).empty();

    $(cardContainerSelector).off('click');

    $(cardContainerSelector).on('click', '.deck-card-img', function (event) {
        $(this).siblings('.card-preview').addClass('show');
        $(this).parent().find('img').addClass('show-hover');
        $(this).parent().find('.multi-hovered-img').addClass('show-hover');
    });

    $(document).off('keyup');

    $(document).on('keyup', function (e) {
        if (e.key === "Escape") {
            $('.card-preview').removeClass('show');
            $('.hover-card-img.show-hover').removeClass('show-hover');
            $('.multi-hovered-img.show-hover').removeClass('show-hover');
        }
    });

    $(cardContainerSelector).off('click');

    $(cardContainerSelector).on('click', '.card-preview', function (e) {
        if (e.target.classList.contains('card-preview')) {
            $(this).removeClass('show');
            $('.hover-card-img.show-hover').removeClass('show-hover');
            $('.multi-hovered-img.show-hover').removeClass('show-hover');
        }
    });

    $(buttonSelector).off('click');

    $(buttonSelector).on('click', function (e) {
        cardsToUse = originalCardStack;
        $(cardContainerSelector).empty();
        const startingHandSize = 5; //we need index
        cardsToUse = randomizeCards(cardsToUse);

        let startHand = cardsToUse.slice(0, startingHandSize)
        cardsToUse = cardsToUse.slice(startingHandSize, cardsToUse.length)
        startHand.forEach(card => {
            $(cardContainerSelector).append(card);
        });

    });

    $(drawButtonSelector).off('click');

    $(drawButtonSelector).on('click', function (e) {
        $(cardContainerSelector).append(cardsToUse[0]);
        cardsToUse = cardsToUse.slice(1, cardsToUse.length)
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
    let htmlCards = [];

    cards.forEach((card) => {
        for (let i = 0; i < card.quantity; i++) {
            htmlCards.push(createHtmlForCard(card));
        }
    });

    return htmlCards;
}

function createHtmlForCard(card) {
    return `
        <div class="deck-card">
            <img class="deck-card-img" src="${card.img}">
            <div class="card-preview">
                <div class="multi-hovered-img">
                    <img class="hover-card-img" src="${card.img}">
                </div>
            </div>
        </div>
    `
}

