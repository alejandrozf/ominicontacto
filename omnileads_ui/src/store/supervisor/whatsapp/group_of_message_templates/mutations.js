export default {
    initWhatsappGroupOfMessageTemplates (state, data) {
        state.supWhatsappGroupOfMessageTemplates = data;
    },
    initWhatsappGroupOfMessageTemplate (state, data = null) {
        if (data) {
            state.supWhatsappGroupOfMessageTemplate = {
                id: data.id,
                nombre: data.nombre,
                plantillas: data.plantillas
            };
        } else {
            state.supWhatsappGroupOfMessageTemplate = {
                id: null,
                nombre: '',
                plantillas: []
            };
        }
    },
    initMessageTemplatesOfGroup (state, data = []) {
        state.supMessageTemplatesOfGroup = data;
    },
    addMessageTemplateToGroup (state, data = null) {
        if (data) {
            state.supMessageTemplatesOfGroup.push(data);
        }
    },
    removeMessageTemplateOfGroup (state, id = null) {
        if (id) {
            state.supMessageTemplatesOfGroup = state.supMessageTemplatesOfGroup.filter(p => p !== id);
        }
    }
};
