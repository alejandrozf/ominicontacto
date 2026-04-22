export default {
    dashboard_home_page: {
        active_campaign_by_type: 'Campañas {type} Activas',
        agent_status: 'Estado de agentes',
        agent_status_oncall: 'En llamada',
        agent_status_pause: 'Pausado',
        agent_status_ready: 'Listo',
        authenticated_agents: 'Agentes Autenticados',
        califications: 'Calificaciones',
        today: 'Hoy',
        yesterday: 'Ayer',
        call_sumary: 'Resumen de llamadas',
        call_sumary_attended: 'Atendidas',
        call_sumary_failed: 'Fallidas'
    },
    add_agents_to_campaign: {
        already_agent_in_campaign: 'El agente ya está en la campaña',
        already_agents_in_campaign: 'Los siguientes agentes ya estaban en la campaña: ( {agents} ), por lo tanto no se agregaron',
        empty_campaign_notice: 'La campaña se quedará sin agentes',
        how_to_edit_penalty: 'Para modificar el penalty selecciona la columna',
        agents_campaign: 'Agentes de campaña',
        agents_not_save: 'No se guardaron los agentes'
    },
    pause_sets: {
        title: 'Conjuntos de pausas',
        configured_pauses: 'Pausas configuradas',
        infinite_pause: 'Pausa infinita',
        pause_settings_will_be_deleted: 'Todas las configuraciones de pausas se van a eliminar',
        pause_sets_not_deleted: 'No se elimino el conjunto de pausas',
        pause_config_not_deleted: 'No se elimino la configuracion de pausa',
        pause_sets_without_pauses: 'No se puede crear un conjunto de pausa sin pausas',
        how_to_edit_pause_setting: 'Para editar las pausas, da click en la celda de Tiempo para terminar pausa'
    },
    pause_setting: {
        max_time_allowed: 'El tiempo maximo de pausa es de 8 horas (28800 segundos)',
        min_time_allowed: 'Tiempo infinito, quiere decir que nunca saldras de la pausa (0 segundos)'
    },
    audit: {
        title: 'Auditoría administrativa'
    },
    external_sites: {
        list_title: 'Sitios Externos',
        show_hiddens: 'Mostrar ocultos',
        remove_hiddens: 'Quitar ocultos',
        hide: 'Ocultar',
        show: 'Desocultar'
    },
    external_site_authentication: {
        test_auth: {
            label: 'Probar Autenticación'
        },
        list_title: 'Autenticaciones para sitios externos',
        edit_title: 'Editar autenticacion para sitio externo',
        new_title: 'Nueva autenticacion para sitio externo'
    },
    call_dispositions: {
        list_title: 'Calificaciones',
        edit_title: 'Edita la calificacion',
        new_title: 'Nueva calificacion',
        add_subcategory: 'Adicionar nueva subcalificación'
    },
    external_system: {
        new_agent_on_system: 'Nuevo agente en sistema',
        edit_agent_on_system: 'Edita agente en sistema'
    },
    form: {
        step1: {
            title: 'Datos del Formulario'
        },
        step2: {
            title: 'Campos del Formulario'
        },
        step3: {
            title: 'Vista previa',
            display_name: 'Nombre:',
            display_description: 'Descripcion:'
        }
    },
    outbound_route: {
        detail_title: 'Informacion de la ruta saliente',
        new_title: 'Nueva ruta saliente',
        edit_title: 'Edita la ruta saliente'
    },
    dial_pattern: {
        new_title: 'Nuevo patron de discado',
        edit_title: 'Edita patron de discado'
    },
    trunk: {
        new_title: 'Nueva troncal',
        edit_title: 'Edita troncal'
    },
    group_of_hour: {
        new_title: 'Nuevo grupo horario',
        edit_title: 'Edita grupo horario'
    },
    time_validation: {
        new_title: 'Nueva validacion de tiempo',
        edit_title: 'Edita validacion de tiempo'
    },
    ivr: {
        new_title: 'Nuevo IVR',
        edit_title: 'Edita el IVR',
        configuration_time_out: 'Configuracion para Time Out',
        configuration_invalid_destination: 'Configuracion para Destino Invalido',
        destinations: {
            time_out: 'Destino para time out',
            invalid: 'Destino invalido'
        },
        audios: {
            types: {
                internal: 'Audio interno',
                external: 'Audio externo'
            },
            main: {
                title: 'Audio principal',
                internal: 'Audio principal interno',
                external: 'Audio principal externo'
            },
            time_out: {
                title: 'Audio timeout',
                internal: 'Audio timeout interno',
                external: 'Audio timeout externo'
            },
            invalid: {
                title: 'Audio invalido',
                internal: 'Audio invalido interno',
                external: 'Audio invalido externo'
            }
        }
    },
    destination_option: {
        new_title: 'Nuevo destino',
        edit_title: 'Edita el destino'
    },
    register_server: {
        title: 'Registro De Instancia',
        info1: 'Gracias por utilizar OMniLeads, la Suite de Contact Center Open Source mas completa y amigable del mercado',
        info2: 'Vaya! Esta instancia aun no esta registrada.',
        info3: 'A partir de este registro, podremos informarte sobre:',
        info4: 'Además, podrás apoyarnos con casos de uso o bugs de software de manera más ágil (podrás solicitar la baja del canal de comunicación en cualquier momento).',
        info5: 'En caso de dudas, contacte a su Administrador.',
        info6: 'Nuevos Releases',
        info7: 'Nuevos Addons',
        info8: 'Ofertas especiales',
        info9: 'Avances de Roadmap',
        info10: 'Articulos de Blogs',
        info11: 'Notas del producto',
        privacy_policies: 'Políticas de privacidad',
        detail: {
            title: 'Gracias por su registro',
            already_register: 'Ya está registrado',
            resend_key: 'Reenviar Key',
            user: 'Usuario',
            http_responses: {
                res1: 'Los datos de la llave fueron enviados con éxito a su email',
                res2: 'No fue posible conectar con el servidor de llaves',
                res3: 'Los datos enviados desde la instancia no son correctos'
            }
        }
    },
    whatsapp: {
        message_template: {
            new_title: 'Nuevo template de mensaje',
            edit_title: 'Edita template de mensaje'
        },
        whatsapp_template: {
            new_title: 'Nuevo template de whatsapp',
            edit_title: 'Edita template de whatsapp'
        },
        provider: {
            new_title: 'Nuevo proveedor',
            edit_title: 'Edita proveedor'
        },
        line: {
            new_title: 'Nueva linea de whatsapp',
            edit_title: 'Edita linea de whatsapp',
            tipos_de_destino: {
                campana: 'Campana',
                interactivo: 'Interactivo',
                flow: 'Flow'
            },
            flow: {
                title: 'Vista Flow del menú interactivo',
                subtitle: 'Este editor gráfico trabaja sobre los mismos bloques y opciones del modo interactivo.',
                open_builder: 'Abrir Flow',
                launch: 'Lanzar',
                add_block: 'Agregar bloque',
                edit_block: 'Editar bloque',
                main: 'Principal',
                untitled_block: 'Bloque sin título',
                empty_body: 'Sin cuerpo configurado',
                blocks: 'bloques',
                options_count: 'opciones',
                editor_help: 'Edita el bloque seleccionado y sus destinos.',
                empty_selection: 'Selecciona un bloque para editarlo.',
                option_label: 'Opción',
                incoming_message: 'Mensaje entrante',
                incoming_help: 'Inicio de la conversación. Desde aquí se deriva al bloque principal del árbol.',
                no_options: 'Sin opciones configuradas',
                no_option_description: 'Sin descripción',
                more_options: 'opciones más',
                drag_help: 'Arrastra los bloques para ordenar el árbol y usa Lanzar para editar cada nodo.',
                cancel_link: 'Cancelar enlace',
                connect: 'Conectar',
                connections: 'Conexiones',
                click_target: 'Haz clic en el bloque destino para unir la flecha.',
                connected_to: 'Conectado a',
                unlinked: 'Sin destino',
                no_links: 'Sin enlaces configurados',
                open_emoji_picker: 'Abrir selector de emojis',
                meta_rows_warning: 'Meta no documenta de forma explícita si el valor y la descripción de cada opción admiten emojis. Se habilitan para prueba, pero conviene validarlo con tu proveedor Meta.',
                preview_time: '09:27',
                default_list_button: 'Elige una opción'
            },
            step1: {
                title: 'Datos basicos'
            },
            step2: {
                title: 'Datos del carrier',
                sender: 'Remitente',
                app_info: 'Info app'
            },
            step3: {
                title: 'Datos de conexion',
                display_name: 'Nombre:',
                display_description: 'Descripcion:',
                message: 'Mensajes',
                destination: 'Destino',
                time_group: 'Grupo horario',
                empty_options: 'Debe existir al menos una opcion de destino'
            },
            option_form: {
                new_title: 'Nueva opcion',
                edit_title: 'Editar opcion'
            }
        },
        group_of_message_template: {
            new_title: 'Nuevo grupo',
            edit_title: 'Edita grupo',
            add_template: 'Agregar template'
        },
        group_of_whatsapp_template: {
            new_title: 'Nuevo grupo',
            edit_title: 'Edita grupo',
            add_template: 'Agregar template'
        },
        disposition_form: {
            form: 'Formulario',
            record: 'Historial',
            management: 'Gestión'
        },
        media_uploader: {
            title: 'Gestión de archivos'
        },
        message_transfer: {
            title: 'Transferir chat'
        },
        conversations: {
            answered: 'Contestados',
            new: 'Nuevos',
            expired_conversation: 'Conversacion expirada',
            restart_conversation: 'Reiniciar conversacion',
            error_conversation_detail: 'No se pudo iniciar la Conversacion de froma correcta',
            error_conversation: 'Conversacion errónea',
            attachment_error_detail: 'Hay adjuntos enviados con error. Código {code}. Contacte al administrador.'
        },
        contact: {
            new: 'Crear contacto',
            edit: 'Editar contacto',
            detail: 'Informacion de contacto',
            info: 'El contacto aun no esta registrado, puedes identificarlo',
            settings: {
                show_info: 'Mostrar informacion',
                edit_info: 'Editar usuario'
            }
        },
        reports: {
            general: {
                title: 'Reporte general de Whatsapp',
                general_report: 'Reporte general',
                sent_messages: 'Mensajes enviados',
                received_messages: 'Mensajes recibidos',
                interactions_started: 'Interacciones iniciadas',
                attended_chats: 'Chats activos',
                not_attended_chats: 'Chats no activos',
                inbound_chats_attended: 'Chats entrantes activos',
                inbound_chats_not_attended: 'Chats entrantes no activos',
                inbound_chats_expired: 'Chats entrantes expirados',
                outbound_chats_attended: 'Chats salientes activos',
                outbound_chats_not_attended: 'Chats salientes no activos',
                outbound_chats_expired: 'Chats salientes expirados',
                outbound_chats_failed: 'Chats salientes fallidos'
            },
            campaign: {
                conversation: {
                    title: 'Reporte de conversaciones',
                    table_title: 'Lista de conversaciones',
                    detail_title: 'Detalle de la conversación',
                    system_closed: 'Cerrada por sistema?',
                    transfer_event: 'Evento de transferencia',
                    transfer_to_agent: 'Transferencia a agente: {agent}',
                    transfer_to_campaign: 'Transferencia a campaña: {campaign}'
                }
            }
        }
    },
    facebook: {
        message_template: {
            new_title: 'New message template',
            edit_title: 'Edit message template'
        },
        facebook_template: {
            new_title: 'New Facebook template',
            edit_title: 'Edit Facebook template'
        },
        page: {
            new_title: 'create facebook page',
            edit_title: 'edit facebook page',
            tipos_de_destino: {
                campana: 'Campaign',
                interactivo: 'Interactive'
            },
            step1: {
                title: 'Basic data'
            },
            step2: {
                title: 'Channel data',
                webhook: 'Webhook',
                page_info: 'Page info'
            },
            step3: {
                title: 'Derivation data',
                display_name: 'Name:',
                display_description: 'Description:',
                message: 'Messages',
                destination: 'Destination',
                time_group: 'Time group',
                empty_options: 'There must be at least one destination option'
            },
            option_form: {
                new_title: 'New option',
                edit_title: 'Edit option'
            }
        },
        group_of_message_template: {
            new_title: 'New group',
            edit_title: 'Edit group',
            add_template: 'Add template'
        },
        group_of_whatsapp_template: {
            new_title: 'New group',
            edit_title: 'Edit group',
            add_template: 'Add template'
        },
        disposition_form: {
            form: 'Form',
            record: 'Record',
            management: 'Management'
        },
        media_uploader: {
            title: 'File management'
        },
        message_transfer: {
            title: 'Transfer chat'
        },
        conversations: {
            answered: 'Answered',
            new: 'New',
            expired_conversation: 'Expired conversation',
            restart_conversation: 'Restart conversation',
            error_conversation_detail: 'Could not start the Conversation correctly',
            error_conversation: 'Wrong conversation',
            anonymous_user: 'Anonymous User'
        },
        contact: {
            new: 'Create contact',
            edit: 'Edit contact',
            detail: 'Contact information',
            info: 'The contact is not yet registered, you can identify it',
            settings: {
                show_info: 'Show information',
                edit_info: 'Edit user'
            }
        },
        reports: {
            general: {
                title: 'WhatsApp general report',
                general_report: 'General report',
                sent_messages: 'Sent messages',
                received_messages: 'Received messages',
                interactions_started: 'Interactions started',
                attended_chats: 'Active chats',
                not_attended_chats: 'Inactive chats',
                inbound_chats_attended: 'Incoming Active chats',
                inbound_chats_not_attended: 'Incoming Inactive chats',
                inbound_chats_expired: 'Expired incoming chats',
                outbound_chats_attended: 'Outbound Active chats',
                outbound_chats_not_attended: 'Outbound Inactive chats',
                outbound_chats_expired: 'Expired outgoing chats',
                outbound_chats_failed: 'Failed outbound chats'
            },
            campaign: {
                conversation: {
                    title: 'Conversation report',
                    table_title: 'Conversation list',
                    detail_title: 'Detail of the conversation',
                    system_closed: 'System Closed?'
                }
            }
        }
    }
};
