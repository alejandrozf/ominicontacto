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
            app_id: '',
            destino: null,
            tipo_de_destino: 0
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
        destinationType: 0,
        destination: null
    },
    supWhatsappLineOptions: [],
    supWhatsappLineIteractiveForm: {
        text: '',
        wrongAnswer: '',
        successAnswer: '',
        timeout: 0,
        options: []
    }
};
