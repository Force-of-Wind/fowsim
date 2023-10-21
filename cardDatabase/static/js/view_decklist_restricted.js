class RestrictionEngine {
    initRestrictions(cardContainer, cardData, restrictions, warningTextOutputElement) {
        if (restrictions === null || restrictions === undefined || restrictions.length < 1 || cardData.length < 1)
            return;

        let registratedRestrictions = [];


        const restrictionFactory = new RestrictionFactory();

        restrictions.forEach(restriction => {
            if(!registratedRestrictions.includes(restriction.action)){
                let restrictionObject = restrictionFactory.getRestrictionForAction(restriction.action, cardContainer, cardData, restriction.checkingTag, restriction.restrictedTag, restriction.text, warningTextOutputElement, restriction.exceptions);
                restrictionObject.applyAction();
                registratedRestrictions.push(restriction.action);
            }
            else
                console.error(`Attempted duplicate registration of restriction ${restriction.action}`);
        });
    }
}

class RestrictionFactory {
    restrictedToZones = ['Ruler', 'Ruler Area', 'Arcana Ruler'];
    ignoredZones = ['Side', 'Side Deck', 'Side Board', 'Side Board Deck', 'Magic', 'Magic Stones', 'Magic Stone Deck'];

    getRestrictionForAction(technicalName, cardContainer, cardData, tagToCheck, restrictedTag, warninigText, warningTextOutputElement, restrictionExceptions) {
        switch (technicalName) {
            case 'conflicting_tag':
                return new ConflictingTagRestriction(cardContainer, cardData, tagToCheck, restrictedTag, warninigText, warningTextOutputElement, restrictionExceptions, [], this.ignoredZones);
            case 'singleton':
                return new SingletonRestriction(cardContainer, cardData, tagToCheck, restrictedTag, warninigText, warningTextOutputElement, restrictionExceptions, this.restrictedToZones, this.ignoredZones);
            case 'arcana_singleton':
                return new ArcanaSingletonRestriction(cardContainer, cardData, tagToCheck, restrictedTag, warninigText, warningTextOutputElement, restrictionExceptions, this.restrictedToZones);
            default:
                console.error(`Restriction ${technicalName} not implemented!`)
                return new BaseRestriction();
        }
    }
}

class BaseRestriction {
    constructor(cardContainer, cardData, tagToCheck, restrictedTag, warninigText, warningTextOutputElement, exceptions = [], restrictedToZones = [], ignoredZones = []) {
        let generatedExceptions = [];
        if(exceptions.length >= 1){
            const factory = new RestrictionExceptionFactory();
            exceptions.forEach((exception) => {
                generatedExceptions.push(factory.getExceptionForType(exception.exceptionAction, exception.exceptionApplyingCard, exception.exceptionApplyingZone, exception.cardsExceptionApplysTo ?? []))
            })
        }

        Object.defineProperties(this, {
            cardContainer: { value: cardContainer},
            tagToCheck: { value: tagToCheck},
            restrictedTag: { value: restrictedTag},
            warninigText: { value: warninigText},
            warningTextOutputElement : { value: warningTextOutputElement},
            restrictedToZones: { value: restrictedToZones},
            ignoredZones: { value: ignoredZones},
            cardData: { value: cardData },
            exceptions: { write:true, value: generatedExceptions},
            differentCardTags: { write:true, value: []},
            cardsForTags: { write:true, value: []},
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

    highlightRestrictedCards = function (affectedCards, tooltip) {
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

class ConflictingTagRestriction extends BaseRestriction {
    applyAction = function() {
        if (this.tagToCheck == null || this.restrictedTag === null)
            return;

        this.initCardData();

        if (this.differentCardTags.includes(this.tagToCheck) && this.differentCardTags.includes(this.restrictedTag)) {

            if(this.exceptions.length >= 1){
                for (let i = 0; i < this.exceptions.length; i++) {
                    const exception = this.exceptions[i];
                    if(exception.isExceptionValid(this.cardData)){
                        if(exception.breakRestriction(this.cardData)){
                            console.info('Ignoring restriction because of full_exception!');
                            return;
                        }
                        else{
                            this.cardsForTags[this.tagToCheck] = exception.filterExceptedCards(this.cardsForTags[this.tagToCheck]);
                            this.cardsForTags[this.restrictedTag] = exception.filterExceptedCards(this.cardsForTags[this.restrictedTag]);
                        }
                    }
                }
            }

            let affectedCards = [];
            affectedCards.push(...this.cardsForTags[this.tagToCheck]);
            affectedCards.push(...this.cardsForTags[this.restrictedTag]);
            if(affectedCards.length <= 1)
                return;
            this.writeWarningTowarningTextOutputElement(this.warninigText);
            this.highlightRestrictedCards(affectedCards.filter(this.distinctFilter), this.warninigText);
        }
    }
}

class SingletonRestriction extends BaseRestriction {
    applyAction = function() {
        this.initCardData();
        const tagIgnoreSingleton = this.restrictedTag;
        if (this.differentCardTags.includes(this.tagToCheck)) {
            let legalSingletonRuler = false;
            let illegalCardsForSingleton = [];
            this.cardsForTags[this.tagToCheck].forEach(card => {
                if (legalSingletonRuler)
                    return;

                if(card.tags.includes(this.tagToCheck) && this.restrictedToZones.includes(card.zone))
                    legalSingletonRuler = true;
            });

            this.cardData.forEach(card => {
                let skip = false;
                if (this.cardsForTags[tagIgnoreSingleton]) {
                    
                    if (card.tags) {
                        card.tags.forEach(tag => {
                            if (skip)
                                return;
                            skip = tag === tagIgnoreSingleton;
                        });
                    }
                }
                if (!skip) {
                    let cardQuantity = card.quantity;
                    let cardZone = card.zone;
                    if (cardQuantity && !isNaN(cardQuantity) && parseInt(cardQuantity) > 1 && !this.ignoredZones.includes(cardZone))
                        illegalCardsForSingleton.push(card);
                }
            });

            if (!legalSingletonRuler)
                return;

                if(this.exceptions.length >= 1){
                    for (let i = 0; i < this.exceptions.length; i++) {
                        const exception = this.exceptions[i];
                        if(exception.isExceptionValid(this.cardData)){
                            if(exception.breakRestriction(this.cardData)){
                                console.info('Ignoring restriction because of full_exception!');
                                return;
                            }
                            else{
                                illegalCardsForSingleton = exception.filterExceptedCards(illegalCardsForSingleton);
                            }
                        }
                    }
                }

            if (illegalCardsForSingleton.length > 0) {
                this.writeWarningTowarningTextOutputElement(this.warninigText);
                this.highlightRestrictedCards(illegalCardsForSingleton, this.warninigText);
            }
        }
    }
}

class ArcanaSingletonRestriction extends SingletonRestriction {

}

class RestrictionExceptionFactory {
    getExceptionForType(type, exceptionApplyingCard, exceptionApplyingZone, applyingToCards){
        switch (type) {
            case 'full_exception':
                return new FullRestrictionException(exceptionApplyingCard, exceptionApplyingZone, applyingToCards);
            case 'partial_exception':
                return new PartialRestrictionException(exceptionApplyingCard, exceptionApplyingZone, applyingToCards);
            default:
                console.error(`Cannot create restriction exception with unknown type ${type}.`);
                break;
        }
    }
}

class BaseRestrictionException {
    constructor(exceptionApplyingCard, exceptionApplyingZone, applyingToCards = []) {
        Object.defineProperties(this, {
            exceptionApplyingCard: { value: exceptionApplyingCard},
            exceptionApplyingZone: { value: exceptionApplyingZone},
            applyingToCards: { value: applyingToCards}
        })
    }

    isExceptionValid = function (cards) 
    { 
        if(cards.length < 1)
            return false;
        
        for (let i = 0; i < cards.length; i++) {
            const card = cards[i];
            if(this.exceptionApplyingZone.split(';').includes(card.zone) && card.id === this.exceptionApplyingCard){
                return true;
            }
        }

        return false;
    }

    breakRestriction = function(){
        return false;
    }
}

class PartialRestrictionException extends BaseRestrictionException {
    filterExceptedCards = function (cards) 
    {
        return cards.filter((card) => !this.applyingToCards.includes(card.id));
    }
}

class FullRestrictionException extends BaseRestrictionException {
    breakRestriction = function(cards){
        return this.isExceptionValid(cards);
    }
}