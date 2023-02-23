export default {
    agent_campaign: {
        name: 'Nombre',
        username: 'Nombre de usuario',
        sip: 'ID SIP',
        penalty: 'Multa'
    },
    pause_set: {
        id: 'ID',
        name: 'Nombre'
    },
    pause_setting: {
        id: 'ID',
        pause: 'Pausa',
        pause_type: 'Tipo de pausa',
        set: 'Conjunto',
        time_to_end_pause: 'Tiempo para terminar pausa'
    },
    audit: {
        user: 'Usuario',
        object: 'Objeto',
        name: 'Nombre',
        action: 'Accion',
        additional_information: 'Información Adicional',
        datetime: 'Fecha y hora'
    },
    external_site: {
        id: 'ID',
        name: 'Nombre',
        url: 'Url',
        method: 'Metodo',
        format: 'Formato',
        objective: 'Objetivo',
        trigger: 'Disparador',
        status: 'Estado'
    },
    external_site_authentication: {
        id: 'ID',
        name: 'Nombre',
        url: 'Url',
        username: 'Username',
        password: 'Contrasena',
        campo_token: 'Campo token',
        duracion: 'Duracion',
        campo_duracion: 'Campo duracion',
        token: 'Token',
        expiracion_token: 'Expiracion del token'
    },
    call_disposition: {
        id: 'ID',
        name: 'Nombre'
    },
    external_system: {
        id: 'ID',
        name: 'Nombre',
        agents: 'Agentes'
    },
    agent_external_system: {
        id: 'ID',
        external_id: 'Id Externo Agente',
        agent: 'Agente'
    },
    form: {
        id: 'ID',
        name: 'Nombre',
        description: 'Descripcion',
        fields: 'Campos',
        status: 'Estado'
    },
    form_field: {
        id: 'ID',
        name: 'Nombre',
        order: 'Orden',
        type: 'Tipo',
        required: 'Es obligatorio',
        list_options: 'Opciones de lista'
    },
    pause: {
        id: 'ID',
        name: 'Nombre',
        type: 'Tipo',
        status: 'Activa'
    },
    inbound_route: {
        id: 'ID',
        name: 'Nombre',
        phone: 'Numero DID',
        caller_id: 'Prefijo',
        idiom: 'Idioma',
        destiny: 'Destino',
        destiny_type: 'Tipo de destino'
    },
    outbound_route: {
        id: 'ID',
        name: 'Nombre',
        ring_time: 'Tiempo de ring',
        dial_options: 'Opciones de discado',
        order: 'Orden'
    },
    dial_pattern: {
        id: 'ID',
        prepend: 'Prepend',
        prefix: 'Prefijo',
        pattern: 'Patron de discado',
        order: 'Orden'
    },
    trunk: {
        id: 'ID',
        name: 'Nombre',
        order: 'Orden'
    },
    group_of_hour: {
        id: 'ID',
        name: 'Nombre',
        time_validations: 'Condiciones de tiempo'
    },
    time_validation: {
        id: 'ID',
        tiempo_inicial: 'Tiempo inicio',
        tiempo_final: 'Tiempo final',
        dia_semana_inicial: 'Dia de la semana inicio',
        dia_semana_final: 'Dia de la semana final',
        dia_mes_inicio: 'Dia del mes inicio',
        dia_mes_final: 'Dia del mes final',
        mes_inicio: 'Mes inicio',
        mes_final: 'Mes final'
    },
    ivr: {
        id: 'ID',
        name: 'Nombre',
        description: 'Descripcion',
        main_audio: 'Audio principal',
        time_out_configuration: {
            time_out: 'Time out',
            retries: 'Intentos time out',
            audio: 'Audio de time out',
            destination: 'Destino time out',
            destination_type: 'Tipo de destino para time out'
        },
        invalid_destination_configuration: {
            retries: 'Intentos invalidos',
            audio: 'Audio de destino invalido',
            destination: 'Destino invalido',
            destination_type: 'Tipo de destino para destino invalido'
        },
        destination_options: 'Opciones de destinos'
    },
    destination_option: {
        id: 'ID',
        dtmf: 'DTMF',
        destination_type: 'Tipo de destino',
        destination: 'Destino'
    },
    register_server: {
        name: 'Nombre o empresa',
        email: 'Correo electrónico',
        password: 'Contraseña de acceso',
        phone: 'Teléfono'
    },
    campaign: {
        types: {
            inbound: 'Entrante',
            manual: 'Manual',
            dialer: 'Dialer',
            preview: 'Preview'
        }
    },
    whatsapp: {
        provider: {
            nombre: 'Nombre',
            tipo_proveedor: 'Proveedor',
            configuracion: {
                api_key: 'API Key'
            }
        },
        line: {
            nombre: 'Nombre',
            proveedor: 'Proveedor',
            numero: 'Número',
            configuracion: {
                app_name: 'App name',
                app_id: 'App ID'
            },
            horario: 'Grupo horario',
            destino: 'Destino',
            tipo_de_destino: 'Tipo de destino',
            mensaje_bienvenida: 'Mensaje de bienvenida',
            mensaje_despedida: 'Mensaje de despedida',
            mensaje_fueradehora: 'Mensaje fuera de horario'
        },
        message_template: {
            nombre: 'Nombre',
            tipo: 'Tipo',
            configuracion: 'Configuracion'
        },
        whatsapp_template: {
            nombre: 'Nombre',
            identificador: 'Identificador',
            texto: 'Texto',
            idioma: 'Idioma',
            status: 'Estado',
            creado: 'Creado',
            modificado: 'Modificado',
            tipo: 'Tipo',
            categoria: 'Categoria'
        }
    }
};
