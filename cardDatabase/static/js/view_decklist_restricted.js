function initRestrictions(cardsWithTags, tagSelector, restrictions, textElement) 
{
    if(restrictions === null || restrictions === undefined || restrictions.length < 1)
        return;

    restrictions.forEach(restriction => {
        applyAction(restriction.action, restriction.checkingTag, restriction.text, restriction.restrictedTag)
    });

    function applyAction(actionName, tagToCheck, warninigText, restrictedTag = null) {
        
        differentCardTags = [];
        cardsForTags = {};;
        cardsWithTags.find(tagSelector).each((index, card) => {
            $(card).data('tags').forEach(tag => {
                if(!differentCardTags.includes(tag))
                    differentCardTags.push(tag);

                if(cardsForTags[tag] !== undefined)
                    cardsForTags[tag] = cardsForTags[tag].push($(card).data('card-id'));
                else
                    cardsForTags[tag] = [$(card).data('card-id')];
            })
        });

        switch (actionName) {
            case 'conflicting_tag':
                handleConflictingTagRestriction(tagToCheck, restrictedTag, differentCardTags, warninigText, cardsForTags);                
                break;
            case 'singelton':
                
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

    function writeWarningToTextElement(warninigText) 
    {
        if(textElement.hasClass('hide-restrictions'))
            textElement.removeClass('hide-restrictions');
        textElement.append(`<p class='warning-text'>${warninigText}</p>`);
    }

    function distinctFilter(value, index, array) {
        return array.indexOf(value) === index;
      }

    function highLightRestrictedCards(affectedCardIds, tooltip) 
    { 
        affectedCardIds.forEach(cardId => {
            cardsWithTags.find(`[data-card-id="${cardId}"]`).each((_, element) => {
                $(element).css('border', '3px solid red');
                $(element).prop('title', tooltip);
            })
        })
    }
}