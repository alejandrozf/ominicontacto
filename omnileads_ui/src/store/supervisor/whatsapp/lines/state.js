export default {
    supWhatsappLines: [],
    supWhatsappLineCampaigns: [],
    supWhatsappLine: {
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
            type: 0
        },
        horario: null,
        mensaje_bienvenida: null,
        mensaje_despedida: null,
        mensaje_fueradehora: null
    },
    isFormToCreate: false,
    supWhatsappLineOptionForm: {
        id: null,
        value: '',
        description: '',
        type_option: 0,
        destination: null,
        destination_name: '',
        menuId: null
    },
    supWhatsappLineOptions: [],
    supWhatsappDestinationMenuOptions: [],
    supWhatsappLineIteractiveForm: {
        id_tmp: 0,
        text: '',
        wrongAnswer: '',
        successAnswer: '',
        timeout: 0,
        options: []
    }
};
