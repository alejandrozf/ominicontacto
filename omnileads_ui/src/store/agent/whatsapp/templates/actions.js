/* eslint-disable no-unused-vars */
// import Service from '@/services/agent/whatsapp/template_service';
// const service = new Service();

export default {
    agtWhatsTemplatesInit ({ commit }) {
        const data = [
            {
                id: 1,
                nombre: 'Plantilla1',
                tipo: 0,
                configuracion: {
                    text: 'Hola Emi, que onda...asdfads',
                    type: 'text'
                }
            },
            {
                id: 2,
                nombre: 'Plantilla2',
                tipo: 1,
                configuracion: {
                    text: 'Hola Mundo',
                    type: 'text'
                }
            },
            {
                id: 3,
                nombre: 'Plantilla1',
                tipo: 0,
                configuracion: {
                    text: 'Hola Emi, que onda...asdfads',
                    type: 'text'
                }
            },
            {
                id: 4,
                nombre: 'Plantilla2',
                tipo: 1,
                configuracion: {
                    text: 'Hola Mundo',
                    type: 'text'
                }
            }
        ];
        commit('agtWhatsTemplatesInit', data);
    },
    async agtWhatsTemplateSendMsg ({ commit }, template) {
        console.log('Send template message: ', template);
        return await {
            status: 'SUCCESS',
            message: 'Template enviado exitosamente'
        };
    }
};
