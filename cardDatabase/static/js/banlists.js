$(function(){
    function switchTab(formatName) {
        // Hide all sections
        $('.format-section').removeClass('active');
        // Show selected section
        
        $(`#section-${formatName}-bans`).addClass('active');
        $(`#section-${formatName}-combination-bans`).addClass('active');

        // Update tab UI
        $('.tab').removeClass('active');
        $(`#tab-${formatName}`).addClass('active');
    }

    // Tab switch handlers
    $('.tab').on('click', function () {
        let formatName = $(this).data('format-name');
        switchTab(formatName);
    });

    // Auto-click the first tab
    $('#tab-wanderer').first().trigger('click');
})
