import { getConfigurationByType } from '@/helpers/supervisor/whatsapp/message_template';

export default {
    initWhatsappMessageTemplates (state, messageTemplates) {
        state.supWhatsappMessageTemplates = messageTemplates;
    },
    initWhatsappMessageTemplate (state, messageTemplate = null) {
        if (messageTemplate) {
            state.supWhatsappMessageTemplate = {
                id: messageTemplate.id,
                nombre: messageTemplate.nombre,
                tipo: messageTemplate.tipo,
                configuracion: getConfigurationByType(messageTemplate.tipo, messageTemplate.configuracion)
            };
        } else {
            state.supWhatsappMessageTemplate = {
                id: null,
                nombre: '',
                tipo: null,
                configuracion: null
            };
        }
    },
    initWhatsappMessageTemplateFormFields (state, { type = null, config = null }) {
        state.supWhatsappMessageTemplateFormFields = getConfigurationByType(type === null ? 0 : type, config);
    }
};
