export default {
    initWhatsappLines (state, lines) {
        state.supWhatsappLines = lines;
    },
    initWhatsappLine (state, line = null) {
        if (line) {
            state.supWhatsappLine = {
                id: line.id,
                nombre: line.name,
                proveedor: line.provider,
                numero: line.number,
                configuracion: {
                    app_name: line.configuration.app_name,
                    app_id: line.configuration.app_id,
                    destino: line.configuration.destino,
                    tipo_de_destino: line.configuration.tipo_de_destino
                },
                horario: line.schedule,
                mensaje_bienvenida: line.welcome_message,
                mensaje_despedida: line.farewell_message,
                mensaje_fueradehora: line.afterhours_message
            };
        } else {
            state.supWhatsappLine = {
                id: null,
                nombre: '',
                proveedor: null,
                numero: '',
                configuracion: {
                    app_name: '',
                    app_id: '',
                    destino: null,
                    tipo_de_destino: 0
                },
                horario: null,
                mensaje_bienvenida: '',
                mensaje_despedida: '',
                mensaje_fueradehora: ''
            };
        }
    },
    initFormFlag (state, flag) {
        state.isFormToCreate = flag;
    },
    initWhatsappLineCampaigns (state, campaigns) {
        state.supWhatsappLineCampaigns = campaigns;
    }
};
