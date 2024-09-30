export default {
    forms: [],
    formDetail: {
        nombre: '',
        descripcion: '',
        campos: [],
        oculto: false
    },
    newForm: {
        id: null,
        nombre: '',
        descripcion: '',
        campos: []
    },
    newFormField: {
        id: null,
        nombre_campo: '',
        orden: null,
        tipo: null,
        tipo_numero: null,
        cifras_significativas: null,
        values_select: null,
        is_required: false
    },
    isFormToCreate: true,
    optionListValues: []
};
