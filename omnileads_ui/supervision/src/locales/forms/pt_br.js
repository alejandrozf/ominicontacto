export default {
    pause_set: {
        new: {
            name: 'Nome do conjunto',
            configured_pauses: 'Pausas configuradas',
            enter_name: 'Digite o nome'
        }
    },
    pause_setting: {
        enter_time: 'Digite a hora',
        infinite_time: 'Tempo infinito'
    },
    call_disposition: {
        enter_name: 'Digite o nome'
    },
    external_system: {
        enter_name: 'Digite o nome'
    },
    form: {
        enter_name: 'Digite o nome',
        enter_description: 'Digite a descrição',
        new_field: 'Novo campo',
        options_list: 'Opções para a lista',
        field: {
            type: {
                text: 'Texto',
                date: 'Fecha',
                list: 'Lista',
                text_box: 'Caja de texto'
            }
        },
        validations: {
            required_name: 'o nome é obrigatório',
            required_description: 'A descrição é obrigatória',
            not_empty_list: 'A lista não pode estar vazia',
            field_already_in_form: 'O campo já existe no formulário',
            option_already_in_list: 'A opção já está na lista',
            not_empty_form_field: 'Deve haver pelo menos um campo no formulário'
        }
    },
    pause: {
        enter_name: 'Digite o nome',
        edit_pause: 'Edite a pausa',
        new_pause: 'nova pausa'
    },
    inbound_route: {
        enter_name: 'Digite o nome',
        enter_phone: 'Digite o DI',
        enter_caller_id: 'Digite o caller id',
        edit_inbound_route: 'Editar a rota de entrada',
        new_inbound_route: 'Nova rota de entrada',
        languages: {
            en: 'Inglês',
            es: 'Espanhol'
        },
        destination_types: {
            campaign: 'Campanha de entrada',
            validation_date: 'Validação de data/hora',
            ivr: 'IVR',
            hangup: 'HangUp',
            id_client: 'Identificador do cliente',
            custom_dst: 'Destino personalizado'
        }
    },
    outbound_route: {
        enter_name: 'Digite o nome',
        enter_ring_time: 'Digite o tempo de toque',
        enter_dial_option: 'Digite a opção de discagem',
        validations: {
            not_empty_dial_patterns: 'Deve haver pelo menos um padrão de discagem',
            not_empty_trunks: 'Deve haver pelo menos um tronco',
            repeated_route_name: 'A rota de saída com esse nome já existe',
            invalid_route_name: 'O nome do caminho é inválido',
            trunk_already_exists: 'O tronco já existe'
        }
    },
    dial_pattern: {
        enter_pattern: 'Digite o padrão'
    },
    group_of_hour: {
        enter_name: 'Digite o nome',
        validations: {
            not_empty_time_validations: 'Deve haver pelo menos uma validação de tempo',
            repeated_group_name: 'Já existe um grupo de tempo com esse nome',
            time_validation_already_exists: 'A validação de tempo já existe'
        },
    },
    external_site_authentication: {
        placeholders: {
            url: 'Ejemplo: https://www.omnileads.net/',
            name: 'Digite o nome',
            username: 'Insira nome de usuário',
            campo_token: 'Digite o nome do campo para o token',
            campo_duracion: 'Digite o nome do campo para a duração',
            duracion: 'Insira a duração'
        },
        helpers: {
            username: 'Sem espaços',
            campo_token: 'Campo em que vem o token de acesso',
            campo_duracion: 'Campo em que vem a duração do token',
            duracion: 'Em segundos'
        },
        validations: {
            name_already_exist: 'Nome já existe',
            invalid_campo_duracion: 'Se não houver duração, o campo de duração deve existir.',
            invalid_name_campo_token: 'O nome do campo de token é inválido',
            invalid_name_campo_duracion: 'O nome do campo de duração é inválido'
        }
    }
};
