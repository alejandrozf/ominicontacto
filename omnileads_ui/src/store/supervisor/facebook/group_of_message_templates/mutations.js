export default {
    initFacebookPageGroupOfMessageTemplates (state, data) {
        state.supFacebookPageGroupOfMessageTemplates = data;
    },
    initFacebookPageGroupOfMessageTemplate (state, data = null) {
        if (data) {
            state.supFacebookPageGroupOfMessageTemplate = {
                id: data.id,
                nombre: data.name,
                plantillas: data.templates
            };
        } else {
            state.supFacebookPageGroupOfMessageTemplate = {
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
