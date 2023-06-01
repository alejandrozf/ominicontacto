export default {
    agent_campaign: {
        name: 'Nome',
        username: 'Username',
        sip: 'ID SIP',
        penalty: 'Multa'
    },
    pause_set: {
        id: 'ID',
        name: 'Nome'
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
        name: 'Nome',
        action: 'Açao',
        additional_information: 'Mudar',
        datetime: 'Data e hora'
    },
    external_site: {
        id: 'ID',
        name: 'Nome',
        url: 'URL',
        method: 'Método',
        format: 'Formato',
        objective: 'Meta',
        trigger: 'Acionar',
        status: 'Doença'
    },
    external_site_authentication: {
        id: 'ID',
        name: 'Nome',
        url: 'Url',
        username: 'Nome de usuário',
        password: 'Senha',
        campo_token: 'Campo token',
        duracion: 'Duração',
        campo_duracion: 'Campo de duração',
        token: 'Token',
        expiracion_token: 'expiração do token'
    },
    call_disposition: {
        id: 'ID',
        name: 'Nome'
    },
    external_system: {
        id: 'ID',
        name: 'Name',
        agents: 'Agents'
    },
    agent_external_system: {
        id: 'ID',
        external_id: 'ID externo do agente',
        agent: 'Agente'
    },
    form: {
        id: 'ID',
        name: 'Nome',
        description: 'Descrição',
        fields: 'Campos',
        status: 'Doença'
    },
    form_field: {
        id: 'ID',
        name: 'Nome',
        order: 'Ordem',
        type: 'Cara',
        required: 'É obrigatório?',
        list_options: 'listar opções'
    },
    pause: {
        id: 'ID',
        name: 'Nome',
        type: 'Cara',
        status: 'Status'
    },
    inbound_route: {
        id: 'ID',
        name: 'Nome',
        phone: 'Número DID',
        caller_id: 'Prefixo',
        idiom: 'Idioma',
        destiny: 'Destino',
        destiny_type: 'Tipo de destino'
    },
    outbound_route: {
        id: 'ID',
        name: 'Nome',
        ring_time: 'hora do toque',
        dial_options: 'opções de discagem',
        order: 'Ordem'
    },
    dial_pattern: {
        id: 'ID',
        prepend: 'Anexar',
        prefix: 'Prefixo',
        pattern: 'padrão de discagem',
        order: 'Ordem'
    },
    trunk: {
        id: 'ID',
        name: 'Nome',
        order: 'Ordem'
    },
    group_of_hour: {
        id: 'ID',
        name: 'Nome',
        time_validations: 'Condições do tempo'
    },
    time_validation: {
        id: 'ID',
        tiempo_inicial: 'Dora de início',
        tiempo_final: 'Hora final',
        dia_semana_inicial: 'Dia de início da semana',
        dia_semana_final: 'Dia da última semana',
        dia_mes_inicio: 'Dia de início do mês',
        dia_mes_final: 'Dia final do mês',
        mes_inicio: 'Mês de início',
        mes_final: 'Fim do mês'
    },
    ivr: {
        id: 'ID',
        name: 'Nome',
        description: 'Descrição',
        main_audio: 'áudio principal',
        time_out_configuration: {
            time_out: 'Tempo esgotado',
            retries: 'Tentativas de tempo limite',
            audio: 'Tempo limite de áudio',
            destination: 'Tempo limite de destino',
            destination_type: 'Tipo de destino para tempo limite'
        },
        invalid_destination_configuration: {
            retries: 'Tentativas inválidas',
            audio: 'Áudio de destino inválido',
            destination: 'Destino inválido',
            destination_type: 'Tipo de destino para destino inválido'
        },
        destination_options: 'Opções de destino'
    },
    destination_option: {
        id: 'ID',
        dtmf: 'DTMF',
        destination_type: 'Tipo de destino',
        destination: 'Destino'
    },
    register_server: {
        name: 'Nome ou empresa',
        email: 'Correio eletrônico',
        password: 'senha de acesso',
        phone: 'Telefone'
    }
};
