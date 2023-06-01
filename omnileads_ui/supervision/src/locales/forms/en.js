export default {
    pause_set: {
        new: {
            name: 'Set name',
            configured_pauses: 'Configured pauses',
            enter_name: 'Enter the name'
        }
    },
    pause_setting: {
        enter_time: 'Enter the time',
        infinite_time: 'Infinite time'
    },
    call_disposition: {
        enter_name: 'Enter the name'
    },
    external_system: {
        enter_name: 'Enter the name'
    },
    form: {
        enter_name: 'Enter the name',
        enter_description: 'Enter the description',
        new_field: 'New Field',
        options_list: 'Options for the list',
        field: {
            type: {
                text: 'Text',
                date: 'Date',
                list: 'List',
                text_box: 'Text box'
            }
        },
        validations: {
            required_name: 'Required name',
            required_description: 'Required description',
            not_empty_list: 'The list cannot be empty',
            field_already_in_form: 'The field already exists in the form',
            option_already_in_list: 'The option is already on the list',
            not_empty_form_field: 'There must be at least one field in the form'
        }
    },
    pause: {
        enter_name: 'Enter the name',
        edit_pause: 'Edit pause',
        new_pause: 'New pause'
    },
    inbound_route: {
        enter_name: 'Enter the name',
        enter_phone: 'Enter DID number',
        enter_caller_id: 'Enter the caller ID prefix',
        edit_inbound_route: 'Inbound route edit',
        new_inbound_route: 'Inbound route new',
        languages: {
            en: 'English',
            es: 'Spanish'
        },
        destination_types: {
            campaign: 'Inbound campaign',
            validation_date: 'Date/time validation',
            ivr: 'IVR',
            hangup: 'HangUp',
            id_client: 'Client ID',
            custom_dst: 'Custom destination'
        }
    },
    outbound_route: {
        enter_name: 'Enter the name',
        enter_ring_time: 'Enter the ring time',
        enter_dial_option: 'Enter the dial option',
        validations: {
            not_empty_dial_patterns: 'There must be at least one dial pattern',
            not_empty_trunks: 'There must be at least one trunk',
            repeated_route_name: 'Outgoing route with that name already exists',
            invalid_route_name: 'The path name is invalid',
            trunk_already_exists: 'Trunk already exists',
            orphan_trunks: 'By eliminating the outgoing route the following Sip Trunks will remain unused by Outgoing routes'
        }
    },
    dial_pattern: {
        enter_pattern: 'Enter the pattern'
    },
    group_of_hour: {
        enter_name: 'Enter the name',
        validations: {
            not_empty_time_validations: 'There must be at least one time validation',
            repeated_group_name: 'There is already a time group with that name',
            time_validation_already_exists: 'The time validation already exists'
        }
    },
    external_site_authentication: {
        placeholders: {
            name: 'Enter name',
            url: 'Example: https://www.omnileads.net/',
            username: 'Enter username',
            campo_token: 'Enter the field name for the token',
            campo_duracion: 'Enter the name of the field for the duration',
            duracion: 'Enter duration'
        },
        helpers: {
            username: 'No spaces',
            campo_token: 'Field in which the access token comes',
            campo_duracion: 'Field in which the duration of the token comes',
            duracion: 'In seconds'
        },
        validations: {
            name_already_exist: 'Name already exists',
            invalid_campo_duracion: 'If there is no duration, the duration field must exist.',
            invalid_name_campo_token: 'The token field name is invalid',
            invalid_name_campo_duracion: 'The duration field name is invalid'
        }
    },
    ivr: {
        enter_name: 'Enter the name',
        enter_description: 'Enter the description',
        validations: {
            not_empty_time_validations: 'There must be at least one time validation',
            repeated_ivr_name: 'IVR with that name already exists',
            destination_option_already_exists: 'Destination option already exists'
        },
        destination_types: {
            campaign: 'Inbound campaign',
            validation_date: 'Date/time validation',
            ivr: 'IVR',
            hangup: 'Hang Up',
            id_client: 'Client identifier',
            custom_dst: 'Custom destination'
        },
        audios: {
            external: {
                drag_and_drop: 'Drag and drop files here to upload'
            },
            validations: {
                required_internal_file: 'Internal file is required',
                required_external_file: 'External file is required'
            }
        }
    },
    destination_option: {
        validations: {
            repeated_dtmf: 'There is already a destination option with that DTMF',
            invalid_dtmf: 'The DTMF value must be a digit (0-9) or a character (#, -, *)'
        }
    },
    register_server: {
        enter_name: 'Enter the name or company',
        enter_password: 'Enter the password',
        enter_email: 'Enter the email',
        enter_phone: 'Example: 5555555555'
    }
};
