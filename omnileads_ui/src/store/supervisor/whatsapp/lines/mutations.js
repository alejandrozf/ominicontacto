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
                destination: {
                    data: line.destination.data,
                    type: line.destination.type
                },
                horario: line.schedule,
                mensaje_bienvenida: line.welcome_message,
                mensaje_despedida: line.farewell_message,
                mensaje_fueradehora: line.afterhours_message
            };
            state.supWhatsappLine.configuracion.destino = line.destination.data;
            if (line.configuration.tipo_de_destino === 1) {
                state.supWhatsappLineOptions = line.destination.data.options;
                for (let i = 0; i < state.supWhatsappLineOptions.length; i++) {
                    state.supWhatsappLineOptions[i].index = i;
                    state.supWhatsappLineOptions[i].destinationType = 0;
                }
            } else {
                state.supWhatsappLineOptions = [];
            }
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
                destination: {
                    data: null,
                    type: 0
                },
                horario: null,
                mensaje_bienvenida: '',
                mensaje_despedida: '',
                mensaje_fueradehora: ''
            };
            state.supWhatsappLineOptions = [];
        }
    },
    initFormFlag (state, flag) {
        state.isFormToCreate = flag;
    },
    initWhatsappLineCampaigns (state, campaigns) {
        state.supWhatsappLineCampaigns = campaigns;
    },
    initWhatsappLineOptionForm (state, option = null) {
        state.supWhatsappLineOptionForm = {
            id: option ? option.id : null,
            index: option ? option.index : null,
            value: option ? option.value : '',
            description: option ? option.description : '',
            destinationType: option ? option.destinationType : 0,
            destination: option ? option.destination : null
        };
    },
    createWhatsappLineOption (state, option) {
        const ultimoElemento = state.supWhatsappLineOptions[state.supWhatsappLineOptions.length - 1];
        state.supWhatsappLineOptions.push({
            index: ultimoElemento ? ultimoElemento.index + 1 : 0,
            id: option.id,
            value: option.value,
            description: option.description,
            destinationType: option.destinationType,
            destination: option.destination
        });
    },
    updateWhatsappLineOption (state, { id, data }) {
        const element = state.supWhatsappLineOptions.find(item => item.index === id);
        if (element) {
            element.value = data.value;
            element.description = data.description;
            element.destinationType = data.destinationType;
            element.destination = data.destination;
        }
    },
    deleteWhatsappLineOption (state, id) {
        const index = state.supWhatsappLineOptions.findIndex(item => item.index === id);
        if (index >= 0) {
            state.supWhatsappLineOptions.splice(index, 1);
        }
    }
};
