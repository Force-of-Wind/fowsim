$(function(){
   $('.deck-card-img').click(function(event){
       $(this).siblings('.card-preview').addClass('show');
   });

    $(document).keyup(function(e){
        if (e.key === "Escape"){
            $('.card-preview').removeClass('show');
        }
    });

    $('.card-preview').click(function(e){
        if (e.target.classList.contains('card-preview')){
            $(this).removeClass('show');
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

    $('#image-container .deck-zone-count').each(function(index){
        let cards = $(this).siblings('.deck-zone-card-container').find('.deck-card');
        $(this).html( `[${cards.length.toString()}]`);
    });

    $('#table-container .deck-zone-count').each(function(index){
        let quantities = $(this).siblings('.deck-zone-card-container').find('.card-quantity');
        let total = 0;
        quantities.each(function(i){
           total += parseInt($(this).html().trim());
        });
        $(this).html(`[${total}]`);
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

    $('#user-deck-table').click(function(e){
        $('#image-container').hide();
        $('#user-deck-images').removeClass('active');

        $('#table-container').show();
        $('#user-deck-table').addClass('active');

    });

    $('#user-deck-images').click(function(e){
        $('#image-container').show();
        $('#user-deck-images').addClass('active');

        $('#table-container').hide();
        $('#user-deck-table').removeClass('active');
    });

    console.log("Test");
    $('.tcgplayer-price').each(function(){
        $(this).toggle();
        $.ajax({
            type: 'POST',
            url: `/price_check/`,
            data: JSON.stringify({
                card_name: $(this).text()
            }),
            success: function (data) {
                console.log(data);
                $(this).html(data['price']);
            },
            error: function (data) {
                $(this).innerHTML = "Not Listed"
            },
            contentType: 'application/json',
        });
        $(this).toggle();
    });
});