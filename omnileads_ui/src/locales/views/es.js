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
        list_title: 'Autenticaciones para sitios externos',
        edit_title: 'Editar autenticacion para sitio externo',
        new_title: 'Nueva autenticacion para sitio externo'
    },
    call_dispositions: {
        list_title: 'Calificaciones',
        edit_title: 'Edita la calificacion',
        new_title: 'Nueva calificacion'
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
                interactivo: 'Interactivo'
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
                destination: 'Destino'
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
            new: 'Nuevos'
        }
    }
};
