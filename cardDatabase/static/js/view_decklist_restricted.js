function initRestrictions(cardContainer, tagSelector, restrictions, textElement) 
{
    const singeltonRulerZones = ['Ruler', 'Ruler Area', 'Arcana Ruler'];
    const singeltonIgnoreZones = ['Side', 'Side Board', 'Side Board Deck', 'Magic', 'Magic Stones', 'Magic Stone Deck']

    if(restrictions === null || restrictions === undefined || restrictions.length < 1)
        return;

    restrictions.forEach(restriction => {
        applyAction(restriction.action, restriction.checkingTag, restriction.text, restriction.restrictedTag)
    });

    function applyAction(actionName, tagToCheck, warninigText, restrictedTag = null) {
        
        differentCardTags = [];
        cardsForTags = {};;
        cardContainer.find(tagSelector).each((index, card) => {
            $(card).data('tags').forEach(tag => {
                if(!differentCardTags.includes(tag))
                    differentCardTags.push(tag);

                let cardId = $(card).data('card-id');

                if(cardsForTags[tag] && cardsForTags[tag].length > 0 && !cardsForTags[tag].includes(cardId))
                    cardsForTags[tag].push(cardId);
                else
                    cardsForTags[tag] = [cardId];
            })
        });

        switch (actionName) {
            case 'conflicting_tag':
                handleConflictingTagRestriction(tagToCheck, restrictedTag, differentCardTags, warninigText, cardsForTags);                
                break;
            case 'singelton':
                handleSingeltonRestriction(tagToCheck, restrictedTag, differentCardTags, warninigText, cardsForTags, singeltonRulerZones, singeltonIgnoreZones)
                break;
            case 'arcana_singelton':
                handleSingeltonRestriction(tagToCheck, restrictedTag, differentCardTags, warninigText, cardsForTags, singeltonRulerZones, [])
                break;
            default:
                break;
        }
    }

    function handleConflictingTagRestriction(tagToCheck, restrictedTag, differentCardTags, warninigText, cardsForTags) 
    {  
        if(tagToCheck == null || restrictedTag === null)
            return;

        if(differentCardTags.includes(tagToCheck) && differentCardTags.includes(restrictedTag)){
            let affectedCards = [];
            affectedCards.push(...cardsForTags[tagToCheck]);
            affectedCards.push(...cardsForTags[restrictedTag]);
            writeWarningToTextElement(warninigText);
            highLightRestrictedCards(affectedCards.filter(distinctFilter), warninigText)
        }
    }

    function handleSingeltonRestriction(tagToCheck, tagIgnoreSingelton, differentCardTags, warninigText, cardsForTags, singeltonRulerZones, singeltonIgnoreZones)
    {
        if(differentCardTags.includes(tagToCheck)){
            let legalSingeltonRuler = false;
            cardsForTags[tagToCheck].forEach(cardId => {
                if(legalSingeltonRuler)
                    return;
                cardContainer.find(`[data-card-id="${cardId}"]`).each((_, element) => {
                    if(singeltonRulerZones.includes($(element).data('card-zone')))
                        legalSingeltonRuler = true;
                });
            });
            if(!legalSingeltonRuler)
                return; // singelton card not in a deck restriction zone
            
            let illegalCardsForSingelton = [];
            
            cardContainer.find('img.deck-card-img').each((_, card) => {
                let skip = false;
                if(cardsForTags[tagIgnoreSingelton] !== undefined){
                if($(card).data('tags')){
                    $(card).data('tags').forEach(tag => {
                        if(skip)
                            return;
                        skip = tag === tagIgnoreSingelton
                    });
                }}

                if(!skip){
                    let cardQuantity = $(card).data('card-quantity');
                    let cardZone = $(card).data('card-zone');
                    if(cardQuantity && !isNaN(cardQuantity) && parseInt(cardQuantity) > 1 && !singeltonIgnoreZones.includes(cardZone))
                        illegalCardsForSingelton.push(card);
                }
            });
            console.log(illegalCardsForSingelton);

            if(illegalCardsForSingelton.length > 0){
                writeWarningToTextElement(warninigText);
                illegalCardsForSingelton.forEach(card => {
                    $(card).css('border', '3px solid red');
                    $(card).prop('title', warninigText);
                })
            }
                
            
        }        
    }

    function writeWarningToTextElement(warninigText) 
    {
        if(textElement.hasClass('hide-restrictions'))
            textElement.removeClass('hide-restrictions');
        textElement.append(`<div class="banned-card"><img class="banned-icon" src="${$('#banned_icon').attr('src')}"><div class="ban-text">${warninigText}</div></div>`);
    }

    function distinctFilter(value, index, array) {
        return array.indexOf(value) === index;
      }

    function highLightRestrictedCards(affectedCardIds, tooltip) 
    { 
        affectedCardIds.forEach(cardId => {
            cardContainer.find(`[data-card-id="${cardId}"]`).each((_, element) => {
                $(element).css('border', '3px solid red');
                $(element).prop('title', tooltip);
            })
        })
    }
}