$(function(){
   $('.deck-card-img').click(function(event){
       $(this).siblings('.card-preview').addClass('show');
       $(this).parent().find('img').addClass('show-hover');
       $(this).parent().find('.multi-hovered-img').addClass('show-hover');
   });

    $(document).keyup(function(e){
        if (e.key === "Escape"){
            $('.card-preview').removeClass('show');
            $('.hover-card-img.show-hover').removeClass('show-hover');
            $('.multi-hovered-img.show-hover').removeClass('show-hover');
        }
    });

    $('.card-preview').click(function(e){
        if (e.target.classList.contains('card-preview')){
            $(this).removeClass('show');
            $('.hover-card-img.show-hover').removeClass('show-hover');
            $('.multi-hovered-img.show-hover').removeClass('show-hover');
        }
    });

    if (!FOWDB_IS_MOBILE) {
        $('.referenced-card').mouseover(function (event) {
            $(this).find('img').addClass('show-hover');
            $(this).find('.multi-hovered-img').addClass('show-hover');
        });

        $('.referenced-card').mouseout(function (event) {
            $(this).find('img').removeClass('show-hover');
            $(this).find('.multi-hovered-img').removeClass('show-hover');
        });
    }

    $('#untap-export').click(function(e){
        $(this).hide();
        $('#untap-list').addClass('show-untap');
    });

    $('#untap-list textarea').focus(function(e){
         this.select();
    });

    $('.deck-zone-count').each(function(index){
        let cards = $(this).siblings('.deck-zone-card-container').find('.deck-card');
        $(this).html( `[${cards.length.toString()}]`);
    });

    function getReferralUrl(){
        return document.location.host + '/deck/' + document.location.pathname.split('/')[2]
    }

    function getCloneCSSFixes(){
        return `
            .deck-zone-card-container{
                justify-content: unset;
            }
            
            .deck-title, .deck-creator-name{
                text-align: unset;
            }
            
            .cloned-title{
                border-bottom: 1px solid rgb(0 0 0 / 16%);
            }
            
            #image-container{
                width: 700px;
            }
        `
    }

    $('#copy-image').click(function(e){
        let toConvert = document.getElementById('image-container');
        let settings = {
            scale: 3,
            allowTaint: false,
            useCORS: true,
            onclone: function(clonedDocument){
                clonedDocument.getElementById('image-container').style.padding = '20px';
                let site_title = clonedDocument.createElement('div');
                site_title.innerHTML = `<div class="cloned-title"><img style="display: inline-block;" id="site-icon" src="${$('#site-icon').attr('src')}"><div style="display: inline-block;">${getReferralUrl()}</div></div>`;
                clonedDocument.getElementById('image-container').prepend(site_title);
                let ssheet = clonedDocument.createElement('style');
                ssheet.innerText = getCloneCSSFixes();
                clonedDocument.head.appendChild(ssheet);
            }
        };

        if (FOWDB_IS_MOBILE){
            settings.windowWidth = '1080px';
        }

        html2canvas(toConvert, settings).then(function(canvas) {
            let link = document.createElement("a");
            let decklist_name = $('.deck-title').html().trim();
            link.download = `${decklist_name ? decklist_name : 'Decklist'}.png`;
            link.href = canvas.toDataURL("image/png");
            link.target = '_blank';
            link.click();
        });
    });

    if($('#delete-share').length > 0){
        $('#delete-share').click(function(e) {
            deleteShareLink();
        });
        $('#copy-share').click(function(e){
            var copyText = document.getElementById("share-link");
            copyText.select();
            copyText.setSelectionRange(0, 99999);
            navigator.clipboard.writeText(copyText.value);
        });
    }
    else if($('#create-share').length > 0){
        $('#create-share').click(function(e){
            createShareLink();
        });
    }

    if ($('#toggle-lock-decklist').length > 0) {
        $('#toggle-lock-decklist').click(function (e) {
            changeDeckListLock()
        });
        
    }

    function createShareLink(){
        $.ajaxSetup({
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        });
        let deckId = document.getElementById('deck-id').value;
        let url = $('#create-share').data('url');
        
        $.ajax({
            type: 'POST',
            url: url,
            data:{},
            success: function () {
                window.location.reload();
            },
            error: function () {
                console.error('Error creating share link!');
            },
            contentType: 'application/json',
        });
    }

    function deleteShareLink(){
        $.ajaxSetup({
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        });
        let deckId = document.getElementById('deck-id').value;
        let url = $('#delete-share').data('url');

        $.ajax({
            type: 'POST',
            url: url,
            data:{},
            success: function () {
                window.location.reload();
            },
            error: function () {
                console.error('Error deleting share link!');
            },
            contentType: 'application/json',
        });
    }

    function changeDeckListLock(){
        $.ajaxSetup({
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        });
        let url = $('#toggle-lock-decklist').data('url');

        $.ajax({
            type: 'POST',
            url: url,
            data:{},
            success: function () {
                window.location.reload();
            },
            error: function () {
                console.error('Error lock/unlocking Decklist!');
            },
            contentType: 'application/json',
        });
    }

    function getCookie(c_name)
    {
        // https://stackoverflow.com/questions/6506897/csrf-token-missing-or-incorrect-while-post-parameter-via-ajax-in-django
        if (document.cookie.length > 0)
        {
            c_start = document.cookie.indexOf(c_name + "=");
            if (c_start != -1)
            {
                c_start = c_start + c_name.length + 1;
                c_end = document.cookie.indexOf(";", c_start);
                if (c_end == -1) c_end = document.cookie.length;
                return unescape(document.cookie.substring(c_start,c_end));
            }
        }
        return "";
    }
});