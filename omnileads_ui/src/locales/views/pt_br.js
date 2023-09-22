export default {
    dashboard_home_page: {
        active_campaign_by_type: 'Campanhas {type} Ativas',
        agent_status: 'Status do agente',
        call_sumary: 'Resumo da chamada'
    },
    add_agents_to_campaign: {
        already_agent_in_campaign: 'O agente já está na campanha',
        already_agents_in_campaign: 'Os seguintes agentes já estavam na campanha: ( {agents} )',
        empty_campaign_notice: 'A campanha ficará sem agentes',
        how_to_edit_penalty: 'Para modificar a penalidade selecione a coluna',
        agents_campaign: 'Agentes de campainha',
        agents_not_save: 'Agentes não salvos'
    },
    pause_sets: {
        title: 'Conjuntos de pausas',
        configured_pauses: 'Pausas configuradas',
        infinite_pause: 'Pausa infinita',
        pause_settings_will_be_deleted: 'Todas as configurações de pausa serão removidas',
        pause_sets_not_deleted: 'Conjunto de pausa não removido',
        pause_config_not_deleted: 'A configuração de pausa não foi removida',
        pause_sets_without_pauses: 'Não é possível criar um conjunto de pausas sem pausas',
        how_to_edit_pause_setting: 'Para editar as pausas, clique na célula Time to end pause'
    },
    pause_setting: {
        max_time_allowed: 'O tempo máximo de pausa é de 8 horas (28800 segundos)',
        min_time_allowed: 'Tempo infinito, significa que você nunca sairá da pausa (0 segundos)'
    },
    audit: {
        title: 'Auditoria administrativa'
    },
    external_sites: {
        list_title: 'Sites Externos',
        show_hiddens: 'mostrar escondido',
        remove_hiddens: 'remover oculto',
        hide: 'Disfarce',
        show: 'mostrar'
    },
    external_site_authentication: {
        list_title: 'Autenticação para sites externos',
        edit_title: 'Editar autenticação para site externo',
        new_title: 'Nova autenticação para site externo'
    },
    call_dispositions: {
        list_title: 'Classificações',
        edit_title: 'Editar a classificação',
        new_title: 'nova classificação'
    },
    external_system: {
        new_agent_on_system: 'Novo agente no sistema',
        edit_agent_on_system: 'Editar agente no sistema'
    },
    form: {
        step1: {
            title: 'Dados do formulário'
        },
        step2: {
            title: 'Campos do Formulario'
        },
        step3: {
            title: 'Vista previa',
            display_name: 'Nome:',
            display_description: 'Descrição:'
        }
    },
    outbound_route: {
        detail_title: 'Informações da rota de saída',
        new_title: 'Nova rota de saída',
        edit_title: 'Editar rota de saída'
    },
    dial_pattern: {
        new_title: 'Novo padrão de discagem',
        edit_title: 'Editar padrão de discagem'
    },
    trunk: {
        new_title: 'Novo tronco',
        edit_title: 'Editar tronco'
    },
    group_of_hour: {
        new_title: 'Novo grupo de tempo',
        edit_title: 'Editar grupo de tempo'
    },
    time_validation: {
        new_title: 'Nova validação de horário',
        edit_title: 'Editar validação de tempo'
    },
    ivr: {
        new_title: 'Nova URA',
        edit_title: 'Edite o IVR',
        configuration_time_out: 'Configurações de tempo limite',
        configuration_invalid_destination: 'Configuração de destino inválida',
        destinations: {
            time_out: 'Destino para tempo limite',
            invalid: 'destino inválido'
        },
        audios: {
            types: {
                internal: 'áudio interno',
                external: 'áudio externo'
            },
            main: {
                title: 'áudio principal',
                internal: 'Áudio principal interno',
                external: 'Áudio principal externo'
            },
            time_out: {
                title: 'Tempo limite de áudio',
                internal: 'Tempo limite de áudio interno',
                external: 'Tempo limite de áudio externo'
            },
            invalid: {
                title: 'áudio inválido',
                internal: 'Áudio interno inválido',
                external: 'Áudio externo inválido'
            }
        }
    },
    destination_option: {
        new_title: 'Novo destino',
        edit_title: 'Editar o destino'
    },
    register_server: {
        title: 'Registro de instância',
        info1: 'Obrigado por usar o OMniLeads, a suíte de Contact Center de código aberto mais completa e amigável do mercado.',
        info2: 'Oh! Esta instância ainda não está registrada',
        info3: 'A partir deste registro, podemos informá-lo sobre',
        info4: 'Além disso, você pode nos apoiar com casos de uso ou bugs de software de forma mais ágil (você pode solicitar o cancelamento do canal de comunicação a qualquer momento',
        info5: 'Em caso de dúvidas, entre em contato com seu Administrador',
        info6: 'Novos lançamentos',
        info7: 'Novos complementos',
        info8: 'Ofertas especiais',
        info9: 'Roteiros',
        info10: 'Artigos de blog',
        info11: 'Notas do produto',
        privacy_policies: 'Políticas de privacidade',
        detail: {
            title: 'Obrigado por sua inscrição',
            already_register: 'Você já está registrado',
            resend_key: 'Reenviar chave',
            user: 'Do utilizador',
            http_responses: {
                res1: 'Os dados da chave foram enviados com sucesso para o seu e-mail',
                res2: 'Falha ao conectar ao servidor de chaves',
                res3: 'Os dados enviados da instância não estão corretos'
            }
        }
    },
    whatsapp: {
        message_template: {
            new_title: 'Novo modelo de mensagem',
            edit_title: 'Editar modelo de mensagem'
        },
        whatsapp_template: {
            new_title: 'Novo modelo de whatsapp',
            edit_title: 'Editar modelo do whatsapp'
        },
        provider: {
            new_title: 'Novo provedor',
            edit_title: 'Editar provedor'
        },
        line: {
            new_title: 'Criar linha whatsapp',
            edit_title: 'Editar linha do whatsapp',
            tipos_de_destino: {
                campana: 'Campainha',
                interactivo: 'Interativo'
            },
            step1: {
                title: 'Datos basicos'
            },
            step2: {
                title: 'Dados da operadora',
                sender: 'Remetente',
                app_info: 'informações do aplicativo'
            },
            step3: {
                title: 'Dados de conexão',
                display_name: 'Nome:',
                display_description: 'Descrição:',
                message: 'Mensagens',
                destination: 'Destino'
            }
        },
        group_of_message_template: {
            new_title: 'Novo grupo',
            edit_title: 'Editar grupo',
            add_template: 'Agregar template'
        },
        group_of_whatsapp_template: {
            new_title: 'Novo grupo',
            edit_title: 'Editar grupo',
            add_template: 'Agregar template'
        },
        disposition_form: {
            form: 'Forma',
            record: 'Registro',
            management: 'Gerenciamento'
        },
        media_uploader: {
            title: 'Gerenciamento de arquivos'
        },
        message_transfer: {
            title: 'Transferir chat'
        },
        conversations: {
            answered: 'respondidas',
            new: 'Novo'
        }
    }
};
