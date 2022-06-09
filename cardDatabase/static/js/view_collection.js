$(function(){
    $('#tableID').DataTable({
        "info": false,
        "stateSave": true,

        /* Set pagination as false or 
        true as per need */
        "paging": true,
          
        /* Name of the file source 
        for data retrieval */
        "ajax": '/api/all_cards',
        "columns": [
            /* Name of the keys from 
            data file source */
            { "data": "name" },
            { "data": "id" },
            { "data": "set" }
        ]
    });
});