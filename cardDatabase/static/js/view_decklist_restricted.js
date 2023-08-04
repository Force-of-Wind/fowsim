class RestrictionEngine {
    initRestrictions(cardContainer, tagSelector, restrictions, warningTextOutputElement) {
        if (restrictions === null || restrictions === undefined || restrictions.length < 1)
            return;


        const restrictionFactory = new RestricitonFactory();
        let differentCardTags = [];
        let cardsForTags = {};
        cardContainer.find(tagSelector).each((_, card) => {
            $(card).data('tags').forEach(tag => {
                if (!differentCardTags.includes(tag))
                    differentCardTags.push(tag);

                let cardId = $(card).data('card-id');

                if (cardsForTags[tag] && cardsForTags[tag].length > 0 && !cardsForTags[tag].includes(cardId))
                    cardsForTags[tag].push(cardId);
                else
                    cardsForTags[tag] = [cardId];
            })
        });

        restrictions.forEach(restriction => {
            let restricitonClass = restrictionFactory.getRestrictionForAction(restriction.action, cardContainer, restriction.checkingTag, restriction.restrictedTag, differentCardTags, restriction.text, warningTextOutputElement, cardsForTags);
            restricitonClass.applyAction();
        });
    }
}

class RestricitonFactory {
    singeltonRulerZones = ['Ruler', 'Ruler Area', 'Arcana Ruler'];
    singeltonIgnoreZones = ['Side', 'Side Board', 'Side Board Deck', 'Magic', 'Magic Stones', 'Magic Stone Deck'];

    getRestrictionForAction(technicalName, cardContainer, tagToCheck, restrictedTag, differentCardTags, warninigText, warningTextOutputElement, cardsForTags) {
        switch (technicalName) {
            case 'conflicting_tag':
                return new ConflictingTagRestriciton(cardContainer, tagToCheck, restrictedTag, differentCardTags, warninigText, warningTextOutputElement, cardsForTags);
            case 'singelton':
                return new SingeltonRestriciton(cardContainer, tagToCheck, restrictedTag, differentCardTags, warninigText, warningTextOutputElement, cardsForTags, this.singeltonRulerZones, this.singeltonIgnoreZones);
            case 'arcana_singelton':
                return new ArcanaSingeltonRestriciton(cardContainer, tagToCheck, restrictedTag, differentCardTags, warninigText, warningTextOutputElement, cardsForTags, this.singeltonRulerZones);
            default:
                console.error(`Restriciton ${technicalName} not implemented!`)
                return new BaseRestriction();
        }
    }
}

class BaseRestriction {
    constructor(cardContainer, tagToCheck, restrictedTag, differentCardTags, warninigText, warningTextOutputElement, cardsForTags, singeltonRulerZones = [], singeltonIgnoreZones = []) {
        Object.defineProperties(this, {
            cardContainer: { value: cardContainer},
            tagToCheck: { value: tagToCheck},
            restrictedTag: { value: restrictedTag},
            differentCardTags: { value: differentCardTags},
            warninigText: { value: warninigText},
            warningTextOutputElement : { value: warningTextOutputElement},
            cardsForTags: { value: cardsForTags},
            singeltonRulerZones: { value: singeltonRulerZones},
            singeltonIgnoreZones: { value: singeltonIgnoreZones}
        })
    }

    applyAction = function() {
        console.error('Function not implemented for Restriction!');
    }

    writeWarningTowarningTextOutputElement = function (warninigText) {
        if (this.warningTextOutputElement.hasClass('hide-restrictions'))
            this.warningTextOutputElement.removeClass('hide-restrictions');

        this.warningTextOutputElement.append(`<div class="banned-card">
                            <img class="banned-icon" src="${$('#banned_icon').attr('src')}">
                            <div class="ban-text">${warninigText}</div>
                        </div>`);
    }

    distinctFilter = function (value, index, array) {
        return array.indexOf(value) === index;
    }

    highLightRestrictedCards = function (affectedCardIds, tooltip) {
        affectedCardIds.forEach(cardId => {
            this.cardContainer.find(`[data-card-id="${cardId}"]`).each((_, element) => {
                $(element).css('border', '3px solid red');
                $(element).prop('title', tooltip);
            })
        })
    }
}

class ConflictingTagRestriciton extends BaseRestriction {
    applyAction = function() {
        if (this.tagToCheck == null || this.restrictedTag === null)
            return;

        if (this.differentCardTags.includes(this.tagToCheck) && this.differentCardTags.includes(this.restrictedTag)) {
            let affectedCards = [];
            affectedCards.push(...this.cardsForTags[this.tagToCheck]);
            affectedCards.push(...this.cardsForTags[this.restrictedTag]);
            this.writeWarningTowarningTextOutputElement(this.warninigText);
            this.highLightRestrictedCards(affectedCards.filter(this.distinctFilter), this.warninigText);
        }
    }
}
class SingeltonRestriciton extends BaseRestriction {
    applyAction = function() {
        const tagIgnoreSingelton = this.restrictedTag;
        if (this.differentCardTags.includes(this.tagToCheck)) {
            let legalSingeltonRuler = false;
            this.cardsForTags[this.tagToCheck].forEach(cardId => {
                if (legalSingeltonRuler)
                    return;
                this.cardContainer.find(`[data-card-id="${cardId}"]`).each((_, element) => {
                    if (this.singeltonRulerZones.includes($(element).data('card-zone')))
                        legalSingeltonRuler = true;
                });
            });
            if (!legalSingeltonRuler)
                return; // singelton card not in a deck restriction zone

            let illegalCardsForSingelton = [];

            this.cardContainer.find('img.deck-card-img').each((_, card) => {
                let skip = false;
                if (this.cardsForTags[tagIgnoreSingelton] !== undefined) {
                    if ($(card).data('tags')) {
                        $(card).data('tags').forEach(tag => {
                            if (skip)
                                return;
                            skip = tag === tagIgnoreSingelton;
                        });
                    }
                }

                if (!skip) {
                    let cardQuantity = $(card).data('card-quantity');
                    let cardZone = $(card).data('card-zone');
                    if (cardQuantity && !isNaN(cardQuantity) && parseInt(cardQuantity) > 1 && !this.singeltonIgnoreZones.includes(cardZone))
                        illegalCardsForSingelton.push(card);
                }
            });

            if (illegalCardsForSingelton.length > 0) {
                this.writeWarningTowarningTextOutputElement(this.warninigText);
                illegalCardsForSingelton.forEach(card => {
                    $(card).css('border', '3px solid red');
                    $(card).prop('title', this.warninigText);
                })
            }
        }
    }
}

class ArcanaSingeltonRestriciton extends SingeltonRestriciton {

}