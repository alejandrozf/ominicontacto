export default {
    pause_set: {
        new: {
            name: 'Nombre del conjunto',
            configured_pauses: 'Pausas configuradas',
            enter_name: 'Ingresa el nombre'
        }
    },
    pause_setting: {
        enter_time: 'Ingresa el tiempo',
        infinite_time: 'Tiempo infinito'
    },
    call_disposition: {
        enter_name: 'Ingresa el nombre'
    },
    external_system: {
        enter_name: 'Ingresa el nombre'
    },
    form: {
        enter_name: 'Ingresa el nombre',
        enter_description: 'Ingresa la descripcion',
        new_field: 'Nuevo campo',
        options_list: 'Opciones para la lista',
        field: {
            type: {
                text: 'Texto',
                date: 'Fecha',
                list: 'Lista',
                text_box: 'Caja de texto'
            }
        },
        validations: {
            required_name: 'El nombre es requerido',
            required_description: 'La descripcion es requerida',
            not_empty_list: 'La lista no puede estar vacia',
            field_already_in_form: 'El campo ya existe en el formulario',
            option_already_in_list: 'La opcion ya esta en la lista',
            not_empty_form_field: 'Debe existir al menos un campo en el formulario'
        }
    },
    pause: {
        enter_name: 'Ingresa el nombre',
        edit_pause: 'Edita la pausa',
        new_pause: 'Nueva pausa'
    },
    inbound_route: {
        enter_name: 'Ingresa el nombre',
        enter_phone: 'Ingresa el DID',
        enter_caller_id: 'Ingresa el prefijo caller ID',
        edit_inbound_route: 'Edita la ruta entrante',
        new_inbound_route: 'Nueva ruta entrante',
        languages: {
            en: 'Inglés',
            es: 'Español'
        },
        destination_types: {
            campaign: 'Campaña entrante',
            validation_date: 'Validación de fecha/hora',
            ivr: 'IVR',
            hangup: 'HangUp',
            id_client: 'Identificador cliente',
            custom_dst: 'Destino personalizado'
        }
    },
    outbound_route: {
        enter_name: 'Ingresa el nombre',
        enter_ring_time: 'Ingresa el tiempo de ring',
        enter_dial_option: 'Ingresa la opcion de discado',
        validations: {
            not_empty_dial_patterns: 'Debe existir al menos un patron de discado',
            not_empty_trunks: 'Debe existir al menos una troncal',
            repeated_route_name: 'Ya existe ruta saliente con ese nombre',
            invalid_route_name: 'El nombre de la ruta es invalido',
            trunk_already_exists: 'Ya existe la troncal',
            orphan_trunks: 'Al eliminar la ruta saliente los siguientes Troncales Sip quedarán sin ser usados por rutas Salientes'
        }
    },
    dial_pattern: {
        enter_pattern: 'Ingresa el patron'
    },
    group_of_hour: {
        enter_name: 'Ingresa el nombre',
        validations: {
            not_empty_time_validations: 'Debe existir al menos una validacion de tiempo',
            repeated_group_name: 'Ya existe grupo horario con ese nombre',
            time_validation_already_exists: 'Ya existe la validacion de tiempo'
        }
    },
    external_site_authentication: {
        placeholders: {
            name: 'Ingresa el nombre',
            url: 'Ejemplo: https://www.omnileads.net/',
            username: 'Ingresa el username',
            campo_token: 'Ingresa el nombre del campo para el token',
            campo_duracion: 'Ingresa el nombre del campo para la duracion',
            duracion: 'Ingresa la duracion'
        },
        helpers: {
            username: 'Sin espacios',
            campo_token: 'Campo en el cual viene el token de acceso',
            campo_duracion: 'Campo en el cual viene la duracion del token',
            duracion: 'En segundos'
        },
        validations: {
            name_already_exist: 'El nombre ya existe',
            invalid_campo_duracion: 'Si no hay duracion debe existir el campo duracion',
            invalid_name_campo_token: 'El nombre del campo token es invalido',
            invalid_name_campo_duracion: 'El nombre del campo duracion es invalido'
        }
    }
};
