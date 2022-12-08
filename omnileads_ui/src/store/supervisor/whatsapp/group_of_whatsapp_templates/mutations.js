export default {
    initWhatsappGroupOfWhatsappTemplates (state, data) {
        state.supWhatsappGroupOfWhatsappTemplates = data;
    },
    initWhatsappGroupOfWhatsappTemplate (state, data = null) {
        if (data) {
            state.supWhatsappGroupOfWhatsappTemplate = {
                id: data.id,
                nombre: data.nombre,
                templates: data.templates
            };
        } else {
            state.supWhatsappGroupOfWhatsappTemplate = {
                id: null,
                nombre: '',
                templates: []
            };
        }
    },
    initWhatsappTemplatesOfGroup (state, data = []) {
        state.supWhatsappTemplatesOfGroup = data;
    },
    addWhatsappTemplateToGroup (state, data = null) {
        if (data) {
            state.supWhatsappTemplatesOfGroup.push(data);
        }
    },
    removeWhatsappTemplateOfGroup (state, id = null) {
        if (id) {
            state.supWhatsappTemplatesOfGroup = state.supWhatsappTemplatesOfGroup.filter(p => p !== id);
        }
    }
};
