$(function(){
    $('#save-collection-button').click(function (event) {
        let collection_data = {
            "cards": [],
        };
        $('.set-collection').each(function(){
            let card_data = {};
            card_data.quantity = $(this).find('.card-quantity').val();
            card_data.id = $(this).find('.card-id').data('card-id');
            collection_data['cards'].push(card_data);
        });
        $.ajax({
            type: 'POST',
            url: `/save_collection/`,
            data: JSON.stringify({
                collection_data: collection_data,
            }),
            success: function (data) {
                window.onbeforeunload = undefined; // Remove warning of unsaved changes
                window.location.assign(`/collection`);
            },
            error: function (data) {
                console.log('Error');
            },
            contentType: 'application/json',
        })
    });
});