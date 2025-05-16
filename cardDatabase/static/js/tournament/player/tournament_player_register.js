$(function () {
    
     
    function evaluateForm(){
        let val = $('#selected_deck').val();

        if(!val && $('.error-text').hasClass('hidden'))
            $('.error-text').removeClass('hidden');
        else if(val && !$('.error-text').hasClass('hidden'))
            $('.error-text').addClass('hidden');
    
    }

    function updateCard(e) {
        let selectedValue = $('#deck-select').val();
        if(!selectedValue || selectedValue < 1)
            return;

        let deckData = $(`#deck-select option[value="${selectedValue}"]`).data();

        lastModified = deckData.lastModified;
        var lastModifiedDateTime = new Date(0); 
        lastModifiedDateTime.setUTCSeconds(lastModified);

        const card = `
            <div class="col-md-4 mt-3">
                <div class="card">
                    <div class="card-body">
                        <img class="card-img" src="${deckData.frontCard}"></img>
                        <h5 class="card-title">${deckData.name}</h5>
                        <div class="mb-2"><strong>Last Update:</strong><span> ${lastModifiedDateTime.toLocaleDateString()}</span></div>
                        <a href="${deckData.url}" target="_blank" class="btn btn-sm btn-info" target="_blank">View Decklist</a>
                    </div>
                </div>
            </div>
        `;

        $('#deck_preview').empty();
        $('#deck_preview').append(card);
        $('#selected_deck').val(selectedValue);

        evaluateForm();
    };
    
    $('#deck-select').on('change', updateCard);
    $('#register-btn').on('click', evaluateForm);
});