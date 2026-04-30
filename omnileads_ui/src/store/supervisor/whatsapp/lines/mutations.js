export default {
    initWhatsappLines (state, lines) {
        state.supWhatsappLines = lines;
    },
    initWhatsappLine (state, line = null) {
        if (line) {
            var configuracion = {};
            if (line.provider_type === 2) {
                configuracion = {
                    app_name: line.configuration.app_name,
                    app_id: line.configuration.app_id,
                    app_secret: line.configuration.app_secret || '',
                    destination_editor_mode: line.configuration.destination_editor_mode,
                    flow_builder_layout: line.configuration.flow_builder_layout || {}
                };
            } else if (line.provider_type === 1) {
                configuracion = {
                    app_name: line.configuration.waba_id,
                    app_id: line.configuration.app_id,
                    verification_token: line.configuration.verification_token,
                    app_secret: line.configuration.app_secret || '',
                    destination_editor_mode: line.configuration.destination_editor_mode,
                    flow_builder_layout: line.configuration.flow_builder_layout || {}
                };
            }
            state.supWhatsappLine = {
                id: line.id,
                nombre: line.name,
                status: line.status,
                proveedor: line.provider,
                provider_type: line.provider_type,
                numero: line.number,
                configuracion: configuracion,
                destination: {
                    data: line.destination ? line.destination.data : null,
                    type: line.destination ? line.destination.type : null,
                    id_tmp: line.destination && line.destination.type === 10 ? line.destination.id : 0
                },
                horario: line.schedule,
                mensaje_bienvenida: line.welcome_message,
                mensaje_despedida: line.farewell_message,
                mensaje_fueradehora: line.afterhours_message
            };
            state.supWhatsappDestinationMenuOptions = line.destination ? line.destination.data : [];
        } else {
            state.supWhatsappLine = {
                id: null,
                nombre: '',
                proveedor: null,
                provider_type: null,
                numero: '',
                configuracion: {
                    app_secret: '',
                    flow_builder_layout: {}
                },
                destination: {
                    data: null,
                    type: 0,
                    id_tmp: 0,
                    is_main: true
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
            index: option ? option.index : 0,
            value: option ? option.value : '',
            description: option ? option.description : '',
            type_option: option ? option.type_option : 0,
            destination: option ? option.destination : null,
            send_message_before_campaign:
                option ? Boolean(option.send_message_before_campaign) : false,
            message_before_campaign:
                option ? option.message_before_campaign : null
        };
    },
    createWhatsappLineOption (state, { data, menuId }) {
        const ultimoElemento = state.supWhatsappLineOptions[state.supWhatsappLineOptions.length - 1];
        const index = ultimoElemento ? ultimoElemento.index + 1 : 0;
        state.supWhatsappLineOptions.push({
            index: index,
            id: index,
            value: data.value,
            description: data.description,
            type_option: data.type_option,
            destination: data.destination,
            send_message_before_campaign: Boolean(data.send_message_before_campaign),
            message_before_campaign: data.message_before_campaign,
            menuId: menuId
        });
        console.log('createWhatsappLineOption >>>', state.supWhatsappLineOptions);
    },
    updateWhatsappLineOption (state, { id, data, menuId }) {
        const destinationOptions = state.supWhatsappLine.destination.data.filter(item => item.id_tmp === menuId);
        const element = destinationOptions[0].options.find(item => item.id === id);
        if (element) {
            element.value = data.value;
            element.description = data.description;
            element.type_option = data.type_option;
            element.destination = data.destination;
            element.send_message_before_campaign = Boolean(data.send_message_before_campaign);
            element.message_before_campaign = data.message_before_campaign;
        }
    },
    deleteWhatsappLineOption (state, { id, menuId }) {
        const destinationOptions = state.supWhatsappLine.destination.data.filter(item => item.id_tmp === menuId);
        destinationOptions[0].options = destinationOptions[0].options.filter(item => item.id !== id);
    }
};
