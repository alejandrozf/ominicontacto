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
    }
};
