import { getConfigurationByType } from '@/helpers/supervisor/whatsapp/message_template';

export default {
    initFacebookPageTemplates (state, messageTemplates) {
        state.supFacebookPageTemplates = messageTemplates;
    },
    initFacebookPageTemplate (state, messageTemplate = null) {
        if (messageTemplate) {
            state.supFacebookPageTemplate = {
                id: messageTemplate.id,
                nombre: messageTemplate.nombre,
                tipo: messageTemplate.tipo,
                configuracion: getConfigurationByType(messageTemplate.tipo, messageTemplate.configuracion)
            };
        } else {
            state.supFacebookPageTemplate = {
                id: null,
                nombre: '',
                tipo: null,
                configuracion: null
            };
        }
    },
    initFacebookPageTemplateFormFields (state, { type = null, config = null }) {
        state.supFacebookPageTemplateFormFields = getConfigurationByType(type === null ? 0 : type, config);
    }
};
