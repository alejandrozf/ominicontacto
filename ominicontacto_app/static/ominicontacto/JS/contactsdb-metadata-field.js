/* global gettext */
/* global initContactsDBMetadataField */

'use strict';
{
    function addField(fieldsContainerElem, name, is_phone, is_external_id) {
        fieldsContainerElem.append(`
            <div class="form-row align-items-center" >
                <div class="col-auto">
                    <input type="text" class="form-control" name="name" placeholder="${gettext('Nombre')}" value="${name}">
                </div>
                <div class="col-auto ml-4">
                    <div class="form-check">
                        <label class="form-check-label">
                            <input class="form-check-input" type="checkbox" name="is-phone" ${is_phone ? 'checked' : ''}>
                            ${gettext('Campos de teléfono')}
                        </label>
                    </div>
                </div>
                <div class="col-auto ml-4">
                    <div class="form-check">
                        <label class="form-check-label">
                            <input class="form-check-input" type="radio" name="is-external-id" ${is_external_id ? 'checked' : ''}>
                            ${gettext('Id externo')}
                        </label>
                    </div>
                </div>
                <div class="col-auto">
                    <button class="btn btn-outline-danger" data-remove-field="">
                        ${gettext('Remover')}
                    </button>
                </div>
            </div>
        `);
    }

    window.initContactsDBMetadataField = function(
        formElem,
        formFieldElem,
        fieldsContainerElem,
        addFieldTriggerElem
    ) {
        const {
            col_id_externo,
            cols_telefono,
            nombres_de_columnas,
            ...restProps
        } = JSON.parse(formFieldElem.val());
        
        nombres_de_columnas.forEach(function(nombre, index) {
            addField(
                fieldsContainerElem,
                nombre,
                cols_telefono.includes(index),
                col_id_externo === index,
            );
        });

        fieldsContainerElem.on('click', '[data-remove-field]', function(event){
            event.preventDefault();
            $(this).parents('.form-row').remove();
        });

        addFieldTriggerElem.on('click', function(event) {
            event.preventDefault();
            addField(fieldsContainerElem, '', false, false);
        });

        formElem.on('submit', function() {
            const formFieldValue = {
                ...restProps,
                nombres_de_columnas: [],
                col_id_externo: null,
                cols_telefono: [],
                cant_col: 0,
            };
            fieldsContainerElem.children().each(function(_, row){
                const name = $(row).find('input[name="name"]').val();
                if (name) {
                    formFieldValue.nombres_de_columnas.push(name);
                    if ($(row).find('input[name="is-phone"]').prop('checked')) {
                        formFieldValue.cols_telefono.push(formFieldValue.cant_col);
                    }
                    if ($(row).find('input[name="is-external-id"]').prop('checked')) {
                        formFieldValue.col_id_externo = formFieldValue.cant_col;
                    }
                    formFieldValue.cant_col += 1;
                }
            });
            formFieldElem.val(JSON.stringify(formFieldValue));
        });

        return {
        };
    };
}

$(document).ready(function(){
    initContactsDBMetadataField(
        $('#wizardForm'),
        $('[name="custom-basedatoscontacto-metadata"'),
        $('.custom-basedatoscontacto-metadata-fields'),
        $('.custom-basedatoscontacto-metadata-fields-add'),
    );
});
