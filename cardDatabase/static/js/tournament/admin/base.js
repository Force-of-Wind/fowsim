function setupAlertify(){
    alertify.defaults.notifier.delay = 2;
    if (FOWDB_IS_MOBILE) {
        alertify.defaults.notifier.position = 'top-left';
    } else {
        alertify.defaults.notifier.position = 'bottom-left';
    }
}


$(document).ready(function () {
    setupAlertify();
});