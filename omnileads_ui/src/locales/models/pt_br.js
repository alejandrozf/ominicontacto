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
            nombre: 'Nome',
            tipo_proveedor: 'Fornecedor',
            configuracion: {
                api_key: 'API Key'
            }
        },
        line: {
            nombre: 'Nome',
            proveedor: 'Fornecedores',
            numero: 'Número',
            configuracion: {
                app_name: 'nome do aplicativo',
                app_id: 'ID do aplicativo'
            },
            horario: 'Grupo de tempo',
            mensaje_fueradehora: 'Mensagem Fora do Horário',
            destino: 'Destino',
            tipo_de_destino: 'Tipo de destino',
            mensaje_bienvenida: 'Mensagem de boas-vindas',
            mensaje_despedida: 'Mensagem de adeus',
            options: {
                value: 'Valor',
                description: 'Descrição',
                destination_type: 'Tipo de destino',
                destination: 'Destino'
            },
            interactive_form: {
                text: 'Texto',
                wrong_answer: 'Resposta incorreta',
                success_answer: 'Resposta de sucesso',
                timeout: 'Tempo de espera',
                options: 'Opções'
            }
        },
        message_template: {
            nombre: 'Nome',
            tipo: 'Tipo',
            configuracion: 'Configuração'
        },
        whatsapp_template: {
            nombre: 'Nome',
            identificador: 'Identificador',
            texto: 'Texto',
            idioma: 'Linguagem',
            status: 'Estado',
            creado: 'Criada',
            modificado: 'Modificado',
            tipo: 'Cara',
            categoria: 'Categoria',
            active: 'Ativo'
        },
        group_of_message_template: {
            nombre: 'Nome',
            plantillas: 'Plantillas',
            status: 'Estado'
        },
        group_of_whatsapp_template: {
            nombre: 'Nome',
            plantillas: 'Plantillas',
            status: 'Estado'
        },
        disposition_form: {
            type: 'Cara',
            option: 'Opção',
            observations: 'Observações',
            phone: 'Telefone',
            agent: 'Agente',
            contact_phone: 'Telefone de contato',
            contact_data: 'Dados de contato',
            campaign: 'Campainha',
            campaign_type: 'Tipo de campanha',
            disposition_option: 'Opção de qualificação',
            disposition: 'Qualificação',
            created_at: 'Data de criação',
            updated_at: 'Última atualização',
            comments: 'Comentários',
            form_response: 'Resposta do formulário'
        },
        message_transfer: {
            from: 'De',
            to: 'Para'
        },
        templates: {
            message_template: 'Modelo de mensagem',
            whatsapp_template: 'Modelo Whatsapp'
        },
        conversation: {
            campaign: 'Campainha',
            campaign_type: 'Tipo de campanha',
            destination: 'Destino',
            client: 'Cliente',
            agent: 'Agente',
            is_active: 'Ativo',
            expire: 'Data de expiração',
            last_interaction: 'Última interação',
            message: 'Número de mensagens',
            line: 'Linha'
        }
    }
};
