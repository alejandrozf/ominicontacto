export default {
    initSupWhatsappTemplates (state, templates) {
        state.supWhatsappTemplates = templates;
    },
    initSupWhatsappTemplate (state, template = null) {
        if (template) {
            state.supWhatsappTemplate = {
                id: template.id
            };
        } else {
            state.supWhatsappTemplate = {
                id: null,
                nombre: '',
                tipo: null
            };
        }
    }
};
