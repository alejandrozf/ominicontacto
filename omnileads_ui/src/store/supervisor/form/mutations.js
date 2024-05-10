export default {
    initForms (state, forms) {
        state.forms = forms;
    },
    initFormDetail (state, form) {
        state.formDetail = form;
    },
    initNewForm (state, form) {
        if (form === null) {
            state.newForm = {
                id: null,
                nombre: '',
                descripcion: '',
                campos: []
            };
        } else {
            state.newForm = {
                id: form.id,
                nombre: form.nombre,
                descripcion: form.descripcion,
                campos: form.campos
            };
        }
    },
    initNewFormField (state, formField) {
        if (formField === null) {
            state.newFormField = {
                id: null,
                nombre_campo: '',
                orden: null,
                tipo: null,
                values_select: null,
                is_required: false
            };
        } else {
            state.newFormField = {
                id: formField.id,
                nombre_campo: formField.nombre_campo,
                orden: formField.orden,
                tipo: formField.tipo,
                values_select: formField.values_select,
                is_required: formField.is_required
            };
        }
    },
    initOptionListValues (state) {
        state.optionListValues = [];
    },
    addValueOption (state, optionValue) {
        var numValues = state.optionListValues.length;
        if (numValues > 0) {
            optionValue.id = state.optionListValues[numValues - 1].id + 1;
        } else {
            optionValue.id = 0;
        }
        state.optionListValues.push(optionValue);
    },
    removeValueOption (state, id) {
        state.optionListValues = state.optionListValues.filter(data => data.id !== id);
    },
    addFormField (state, formField) {
        state.newForm.campos.push(formField);
    },
    removeFormField (state, formField) {
        state.newForm.campos.filter(function (campo) {
            if (campo.orden > formField.orden) {
                campo.orden -= 1;
            }
        });
        state.newForm.campos = state.newForm.campos.filter(data => !(data.nombre_campo === formField.nombre_campo && data.tipo === formField.tipo));
    },
    initFormToCreateFlag (state, flag = true) {
        state.isFormToCreate = flag;
    }
};
