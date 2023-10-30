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
    external_site: {
        methods: {
            post: 'POST',
            get: 'GET'
        },
        triggers: {
            opt1: 'Agente',
            opt2: 'Automático',
            opt3: 'Servidor',
            opt4: 'Qualificação'
        },
        objectives: {
            opt1: 'Embutido',
            opt2: 'Nova aba'
        },
        formats: {
            opt1: 'multipart/form-data',
            opt2: 'application/x-www-form-urlencoded',
            opt3: 'text/plain',
            opt4: 'application/json'
        }
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
            not_empty_form_field: 'Deve haver pelo menos um campo no formulário',
            repeated_form_name: 'Já existe um formulário com esse nome'
        }
    },
    pause: {
        enter_name: 'Digite o nome',
        edit_pause: 'Edite a pausa',
        new_pause: 'nova pausa',
        validations: {
            repeated_pause_name: 'Já existe uma pausa com esse nome'
        },
        types: {
            opt1: 'Productiva',
            opt2: 'Recreativa'
        }
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
        on_row_reorder: 'Rotas reordenadas, para finalizar a mudança execute a ação reordenar',
        validations: {
            not_empty_dial_patterns: 'Deve haver pelo menos um padrão de discagem',
            not_empty_trunks: 'Deve haver pelo menos um tronco',
            repeated_route_name: 'A rota de saída com esse nome já existe',
            invalid_route_name: 'O nome do caminho é inválido',
            trunk_already_exists: 'O tronco já existe',
            orphan_trunks: 'Ao eliminar a rota de saída, os seguintes Sip Trunks permanecerão sem uso pelas rotas de saída',
            repeated_dial_pattern_prefix: 'Já existe um padrão de discagem com esse prefixo',
            repeated_dial_pattern_rule: 'Já existe um padrão de discagem com essa regra'
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
        }
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
    },
    ivr: {
        enter_name: 'Digite o nome',
        enter_description: 'Digite a descrição',
        validations: {
            not_empty_time_validations: 'Deve haver pelo menos uma validação de tempo',
            repeated_ivr_name: 'IVR com esse nome já existe',
            destination_option_already_exists: 'A opção de destino já existe'
        },
        destination_types: {
            campaign: 'Campanha de entrada',
            validation_date: 'Validação de data/hora',
            ivr: 'IVR',
            hangup: 'desligar',
            id_client: 'Identificador do cliente',
            custom_dst: 'Destino personalizado'
        },
        audios: {
            external: {
                drag_and_drop: 'Arraste e solte os arquivos aqui para fazer upload'
            },
            validations: {
                required_internal_file: 'O arquivo interno é obrigatório',
                required_external_file: 'O arquivo externo é obrigatório'
            }
        }
    },
    destination_option: {
        validations: {
            repeated_dtmf: 'Já existe uma opção de destino com esse DTMF',
            invalid_dtmf: 'O valor DTMF deve ser um dígito (0-9) ou um caractere (#, -, *)'
        }
    },
    register_server: {
        enter_name: 'Digite o nome ou empresa',
        enter_password: 'Digite a senha',
        enter_email: 'Digite o e-mail',
        enter_phone: 'Exemplo: 5555555555',
        validations: {
            forbidden: 'Você não tem permissões para registrar a instância. Entre em contato com seu administrador'
        }
    },
    whatsapp: {
        provider: {
            types: {
                twilio: 'Twilio',
                meta: 'Meta',
                gupshup: 'GupShup'
            }
        },
        message_template: {
            types: {
                text: 'Texto',
                image: 'Cenário',
                file: 'Arquivo',
                audio: 'áudio',
                video: 'Vídeo',
                sticker: 'adesivos',
                location: 'Localização',
                contact: 'Contato'
            },
            fields: {
                text: 'Texto',
                url: 'URL',
                preview_url: 'URL anterior',
                caption: 'Rubrica',
                filename: 'Nome do arquivo',
                longitude: 'Comprimento',
                latitude: 'Latitude',
                name: 'Nome',
                address: 'Direção'
            },
            help_text: {
                audio: {
                    url: 'URL pública do arquivo de áudio'
                },
                image: {
                    original_url: 'URL público da imagem hospedada',
                    preview_url: 'URL público da miniatura da imagem',
                    caption: 'Legenda da imagem'
                },
                file: {
                    url: 'URL pública do arquivo hospedado',
                    filename: 'Nome do arquivo'
                },
                video: {
                    url: 'URL público do arquivo de vídeo',
                    caption: 'Legenda do vídeo'
                },
                sticker: {
                    url: 'URL pública do arquivo de figurinhas'
                }
            }
        },
        line: {
            validations: {
                field_is_required: '{field} é necessário'
            }
        },
        group_of_message_template: {
            validations: {
                not_empty_templates: 'Deve haver pelo menos um modelo'
            }
        },
        group_of_whatsapp_template: {
            validations: {
                not_empty_templates: 'Deve haver pelo menos um modelo'
            }
        },
        contact: {
            validations: {
                field_is_required: '{field} é necessário',
                invalid_field: '{field} tem um formato inválido'
            }
        }
    }
};
