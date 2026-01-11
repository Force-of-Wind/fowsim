var $ = django.jQuery;

function handleImagePreview(evt) {
	console.log("something")
    let fl_files = evt.target.files;
    let fl_file = fl_files[0];

    $('.field-card_image_preview img').prop('src', URL.createObjectURL(fl_file));
}

$( document ).ready(function() {
    $('#id__card_image').on('change', handleImagePreview);
});