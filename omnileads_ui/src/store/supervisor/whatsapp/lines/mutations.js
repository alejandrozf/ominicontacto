export default {
    initWhatsappLines (state, lines) {
        state.supWhatsappLines = lines;
    },
    initWhatsappLine (state, line = null) {
        if (line) {
            console.log('line', line)
            state.supWhatsappLine = {
                id: line.id,
                nombre: line.name,
                proveedor: line.provider,
                numero: line.number,
                configuracion: {
                    app_name: line.configuration.app_name,
                    app_id: line.configuration.app_id,
                },
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
            state.supWhatsappDestinationMenuOptions = line.destination ? line.destination.data : []
        } else {
            state.supWhatsappLine = {
                id: null,
                nombre: '',
                proveedor: null,
                numero: '',
                configuracion: {
                    app_name: '',
                    app_id: ''
                },
                destination: {
                    data: null,
                    type: 0,
                    id_tmp: 0
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
        console.log("option>>>>>", option)
        state.supWhatsappLineOptionForm = {
            id: option ? option.id : null,
            index: option ? option.index : 0,
            value: option ? option.value : '',
            description: option ? option.description : '',
            type_option: option ? option.type_option : 0,
            destination: option ? option.destination : null,
            // destination_name: option ? option.destination.text : '',
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
            menuId: menuId,
        });
        console.log('createWhatsappLineOption >>>', state.supWhatsappLineOptions)
    },
    updateWhatsappLineOption (state, { id, data, menuId }) {
        console.log('index >>>', id)
        const destinationOptions = state.supWhatsappLine.destination.data.filter(item => item.id_tmp === menuId);
        const element = destinationOptions[0].options.find(item => item.id === id);
        if (element) {
            element.value = data.value;
            element.description = data.description;
            element.type_option = data.type_option;
            element.destination = data.destination;
        }
    },
    deleteWhatsappLineOption (state, { id, menuId }) {
        const destinationOptions = state.supWhatsappLine.destination.data.filter(item => item.id_tmp === menuId);
        destinationOptions[0].options = destinationOptions[0].options.filter(item => item.id !== id);
    }
};
