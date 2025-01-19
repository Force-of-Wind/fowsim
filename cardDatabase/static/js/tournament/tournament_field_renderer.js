function renderFields(fields, edit){
    fields.array.forEach(field => {
        
    });
}

function renderEditField(field) { 
    switch (field.type) {
        case 'text':
            return
            `
                <label for="${field.name}">${field.label}</label>
                <input id="${field.name}" maxlength="${field.maxlength}" type="text" name="${field.name}" class="${field.class}"/>
            `;
            break;
        case 'textarea':
            return
            `
                <label for="${field.name}">${field.label}</label>
                <textarea id="${field.name}" maxlength="${field.maxlength}" name="${field.name}" class="${field.class}"/>
            `;
            break;
    
        default:
            break;
    }
}

function renderViewField(field){

}