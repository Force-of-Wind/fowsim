function initSearch(){

    $('#other-pages-bottom').html($('#other-pages-top').html());
    $('.pagination a').each(function(index){
        let page_num = $(this).data('page-index');
        if (page_num) {
            let href = new URL(window.location.href);
            href.searchParams.set('page', page_num);
            $(this).attr('href', href);
        }
    });
}
$(function(){
    initSearch();
});