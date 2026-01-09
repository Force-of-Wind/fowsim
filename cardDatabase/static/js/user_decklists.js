$(document).ready(function() {
    // Initialize MDB select for format filter
    $('.format-filter .mdb-select').materialSelect({
        'visibleOptions': 14,
        'placeholder': 'Search Format(s)...',
        'maxSelectedOptions': 2
    });

    // Delete deck handler
    $('.delete-deck').on('click', function(e) {
        e.preventDefault();
        const deckId = $(this).data('deck-id');
        const deckName = $(this).data('deck-name');

        if (confirm(`Are you sure you want to delete "${deckName}"? This cannot be undone.`)) {
            // Send DELETE request
            $.ajax({
                url: `/delete_decklist/${deckId}/`,
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                success: function() {
                    // Reload page to show updated list
                    window.location.reload();
                },
                error: function() {
                    alert('Error deleting deck. Please try again.');
                }
            });
        }
    });

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Add hasHover class for non-mobile devices
    if (!FOWDB_IS_MOBILE) {
        $('body').addClass('hasHover');
    }

    // Note: search.js handles pagination automatically via data-page-index attributes
    // It preserves all query parameters when navigating between pages
});
