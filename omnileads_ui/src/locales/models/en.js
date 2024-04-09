export default {
    agent_campaign: {
        name: 'Name',
        username: 'Username',
        sip: 'ID SIP',
        penalty: 'Penalty'
    },
    pause_set: {
        id: 'ID',
        name: 'Name'
    },
    pause_setting: {
        id: 'ID',
        pause: 'Pause',
        pause_type: 'Pause type',
        set: 'Set',
        time_to_end_pause: 'Time to end pause'
    },
    audit: {
        user: 'User',
        object: 'Object',
        name: 'Name',
        action: 'Action',
        additional_information: 'Additional Information',
        datetime: 'Datetime'
    },
    external_site: {
        id: 'ID',
        name: 'Name',
        url: 'Url',
        method: 'Method',
        format: 'Format',
        objective: 'Objective',
        trigger: 'Trigger',
        status: 'Status'
    },
    external_site_authentication: {
        id: 'ID',
        name: 'Name',
        url: 'Url',
        username: 'Username',
        password: 'Password',
        campo_token: 'Token field',
        duracion: 'Duration',
        campo_duracion: 'Duration field',
        token: 'Token',
        expiracion_token: 'Token expiration'
    },
    call_disposition: {
        id: 'ID',
        name: 'Name'
    },
    external_system: {
        id: 'ID',
        name: 'Name',
        agents: 'Agents'
    },
    agent_external_system: {
        id: 'ID',
        external_id: 'Id Externo Agente',
        agent: 'Agent'
    },
    form: {
        id: 'ID',
        name: 'Name',
        description: 'Description',
        fields: 'Fields',
        status: 'Status'
    },
    form_field: {
        id: 'ID',
        name: 'Name',
        order: 'Order',
        type: 'Type',
        required: 'Required?',
        list_options: 'List options'
    },
    pause: {
        id: 'ID',
        name: 'Name',
        type: 'Type',
        status: 'Active'
    },
    inbound_route: {
        id: 'ID',
        name: 'Name',
        phone: 'Number DID',
        caller_id: 'Caller Id',
        idiom: 'Language',
        destiny: 'Destiny',
        destiny_type: 'Destiny type'
    },
    outbound_route: {
        id: 'ID',
        name: 'Name',
        ring_time: 'Ring time',
        dial_options: 'Dial options',
        order: 'Order'
    },
    dial_pattern: {
        id: 'ID',
        prepend: 'Prepend',
        prefix: 'Prefix',
        pattern: 'Pattern',
        order: 'Order'
    },
    trunk: {
        id: 'ID',
        name: 'Name',
        order: 'Order'
    },
    group_of_hour: {
        id: 'ID',
        name: 'Name',
        time_validations: 'Time validations'
    },
    time_validation: {
        id: 'ID',
        tiempo_inicial: 'Start time',
        tiempo_final: 'End time',
        dia_semana_inicial: 'Start day of the week',
        dia_semana_final: 'End day of the week',
        dia_mes_inicio: 'Start day of the month',
        dia_mes_final: 'End day of the month',
        mes_inicio: 'Start month',
        mes_final: 'End month'
    },
    ivr: {
        id: 'ID',
        name: 'Name',
        description: 'Description',
        main_audio: 'Main audio',
        time_out_configuration: {
            time_out: 'Time out',
            retries: 'Time out retries',
            audio: 'Time out audio',
            destination: 'Time out destination',
            destination_type: 'Time out destination'
        },
        invalid_destination_configuration: {
            retries: 'Invalid retries',
            audio: 'Invalid audio',
            destination: 'Invalid destination',
            destination_type: 'Invalid destination type'
        },
        destination_options: 'Destination Options'
    },
    destination_option: {
        id: 'ID',
        dtmf: 'DTMF',
        destination_type: 'Destination type',
        destination: 'Destination'
    },
    register_server: {
        name: 'Name or company',
        email: 'Email',
        password: 'Access password',
        phone: 'Phone'
    },
    campaign: {
        types: {
            inbound: 'Inbound',
            manual: 'Manual',
            dialer: 'Dialer',
            preview: 'Preview'
        }
    },
    whatsapp: {
        provider: {
            nombre: 'Name',
            tipo_proveedor: 'Provider',
            configuracion: {
                api_key: 'API Key'
            }
        },
        line: {
            nombre: 'Name',
            proveedor: 'Provider',
            numero: 'Number',
            configuracion: {
                app_name: 'App name',
                app_id: 'App ID'
            },
            horario: 'Group of hour',
            mensaje_fueradehora: 'After Hours Message',
            destino: 'Destiny',
            tipo_de_destino: 'Destination type',
            mensaje_bienvenida: 'Welcome message',
            mensaje_despedida: 'Goodbye message',
            options: {
                value: 'Value',
                description: 'Description',
                destination_type: 'Destination Type',
                destination: 'Destination'
            },
            interactive_form: {
                text: 'Text',
                wrong_answer: 'Wrong answer',
                success_answer: 'Success response',
                timeout: 'Wait time',
                options: 'Options'
            }
        },
        message_template: {
            nombre: 'Nombre',
            tipo: 'Type',
            configuracion: 'Configuration'
        },
        whatsapp_template: {
            nombre: 'Name',
            identificador: 'Identificador',
            texto: 'Text',
            idioma: 'Language',
            status: 'Status',
            creado: 'Created at',
            modificado: 'Updated at',
            tipo: 'Type',
            categoria: 'Category',
            active: 'Active'
        },
        group_of_message_template: {
            nombre: 'Name',
            plantillas: 'Templates',
            status: 'Status'
        },
        group_of_whatsapp_template: {
            nombre: 'Name',
            templates: 'Templates',
            status: 'Status'
        },
        disposition_form: {
            type: 'Type',
            option: 'Option',
            observations: 'Observations',
            phone: 'Phone',
            agent: 'Agent',
            contact_phone: 'Contact Tel',
            contact_data: 'Contact information',
            campaign: 'Bell',
            campaign_type: 'Campaign type',
            disposition_option: 'Qualification option',
            disposition: 'Qualification',
            created_at: 'Creation date',
            updated_at: 'Last update',
            comments: 'Comments',
            form_response: 'Form response'
        },
        message_transfer: {
            from: 'From',
            to: 'To'
        },
        templates: {
            message_template: 'Message template',
            whatsapp_template: 'Whatsapp template'
        },
        conversation: {
            campaign: 'Campaign',
            campaign_type: 'Campaign type',
            destination: 'Destination',
            client: 'Customer',
            agent: 'Agent',
            is_active: 'Is active?',
            last_interaction: 'Last interaction',
            expire: 'Expiration date',
            message: 'Messages number',
            disposition: 'Disposition',
            line: 'Line',
            new: {
                title: 'New conversation',
                model: {
                    campaign: 'Campaign',
                    contact: 'Contact',
                    template: 'Template'
                }
            }
        }
    }
};
