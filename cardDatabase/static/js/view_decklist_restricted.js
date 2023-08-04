class RestrictionEngine {
    initRestrictions(cardContainer, cardData, restrictions, warningTextOutputElement) {
        if (restrictions === null || restrictions === undefined || restrictions.length < 1 || cardData.length < 1)
            return;

        let registratedRestrictions = [];


        const restrictionFactory = new RestricitonFactory();

        restrictions.forEach(restriction => {
            if(!registratedRestrictions.includes(restriction.action)){
                let restrictionObject = restrictionFactory.getRestrictionForAction(restriction.action, cardContainer, cardData, restriction.checkingTag, restriction.restrictedTag, restriction.text, warningTextOutputElement);
                restrictionObject.applyAction();
                registratedRestrictions.push(restriction.action);
            }
            else
                console.error(`Attempted duplicate registration of restriction ${restriction.action}`);
        });
    }
}

class RestricitonFactory {
    restrictedToZones = ['Ruler', 'Ruler Area', 'Arcana Ruler'];
    ignoredZones = ['Side', 'Side Deck', 'Side Board', 'Side Board Deck', 'Magic', 'Magic Stones', 'Magic Stone Deck'];

    getRestrictionForAction(technicalName, cardContainer, cardData, tagToCheck, restrictedTag, warninigText, warningTextOutputElement) {
        switch (technicalName) {
            case 'conflicting_tag':
                return new ConflictingTagRestriciton(cardContainer, cardData, tagToCheck, restrictedTag, warninigText, warningTextOutputElement, [], this.ignoredZones);
            case 'singelton':
                return new SingeltonRestriciton(cardContainer, cardData, tagToCheck, restrictedTag, warninigText, warningTextOutputElement, this.restrictedToZones, this.ignoredZones);
            case 'arcana_singelton':
                return new ArcanaSingeltonRestriciton(cardContainer, cardData, tagToCheck, restrictedTag, warninigText, warningTextOutputElement, this.restrictedToZones);
            default:
                console.error(`Restriciton ${technicalName} not implemented!`)
                return new BaseRestriction();
        }
    }
}

class BaseRestriction {
    constructor(cardContainer, cardData, tagToCheck, restrictedTag, warninigText, warningTextOutputElement, restrictedToZones = [], ignoredZones = []) {
        Object.defineProperties(this, {
            cardContainer: { value: cardContainer},
            tagToCheck: { value: tagToCheck},
            restrictedTag: { value: restrictedTag},
            warninigText: { value: warninigText},
            warningTextOutputElement : { value: warningTextOutputElement},
            restrictedToZones: { value: restrictedToZones},
            ignoredZones: { value: ignoredZones},
            cardData: { value: cardData },
            differentCardTags: { write:true, value: []},
            cardsForTags: { write:true, value: []}
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

    highLightRestrictedCards = function (affectedCards, tooltip) {
        affectedCards.forEach(card => {
            this.cardContainer.find(`[data-card-id="${card.id}"][data-card-zone="${card.zone}"]`).each((_, element) => {
                $(element).css('border', '3px solid red');
                $(element).prop('title', tooltip);
            })
        })
    }

    initCardData = function () 
    {
        this.cardData.forEach(card => {
            if(!this.ignoredZones.includes(card.zone))
            {
                if(card.tags.length > 0){
                    card.tags.forEach(tag => {
                        if (!this.differentCardTags.includes(tag))
                            this.differentCardTags.push(tag);
                        
                        
                        if (this.cardsForTags[tag] && this.cardsForTags[tag].length > 0 && !this.cardsForTags[tag].includes(card.id))
                            this.cardsForTags[tag].push({id: card.id, zone: card.zone, tags: card.tags, quantity: card.quantity});
                        else
                            this.cardsForTags[tag] = [{id :card.id, zone: card.zone, tags: card.tags, quantity: card.quantity}];
                    });
                }
            }
        });

    }
}

class ConflictingTagRestriciton extends BaseRestriction {
    applyAction = function() {
        if (this.tagToCheck == null || this.restrictedTag === null)
            return;

        this.initCardData();

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
        this.initCardData();
        const tagIgnoreSingelton = this.restrictedTag;
        if (this.differentCardTags.includes(this.tagToCheck)) {
            let legalSingeltonRuler = false;
            let illegalCardsForSingelton = [];
            this.cardsForTags[this.tagToCheck].forEach(card => {
                if (legalSingeltonRuler)
                    return;

                if(card.tags.includes(this.tagToCheck) && this.restrictedToZones.includes(card.zone))
                    legalSingeltonRuler = true;
            });

            this.cardData.forEach(card => {
                let skip = false;
                if (this.cardsForTags[tagIgnoreSingelton]) {
                    
                    if (card.tags) {
                        card.tags.forEach(tag => {
                            if (skip)
                                return;
                            skip = tag === tagIgnoreSingelton;
                        });
                    }
                }
                if (!skip) {
                    let cardQuantity = card.quantity;
                    let cardZone = card.zone;
                    if (cardQuantity && !isNaN(cardQuantity) && parseInt(cardQuantity) > 1 && !this.ignoredZones.includes(cardZone))
                        illegalCardsForSingelton.push(card);
                }
            });

            if (!legalSingeltonRuler)
                return;

            if (illegalCardsForSingelton.length > 0) {
                this.writeWarningTowarningTextOutputElement(this.warninigText);
                this.highLightRestrictedCards(illegalCardsForSingelton, this.warninigText);
            }
        }
    }
}

class ArcanaSingeltonRestriciton extends SingeltonRestriciton {

}