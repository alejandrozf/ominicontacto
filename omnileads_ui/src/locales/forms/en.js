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
        enter_name: 'Enter the name',
        enter_subdisposition: 'Enter the subdisposition'
    },
    external_system: {
        enter_name: 'Enter the name'
    },
    external_site: {
        methods: {
            post: 'POST',
            get: 'GET'
        },
        triggers: {
            opt1: 'Agent',
            opt2: 'Automatic',
            opt3: 'Server',
            opt4: 'Call disposition',
            opt5: 'Dynamic list'
        },
        objectives: {
            opt1: 'Embedded',
            opt2: 'New tab'
        },
        formats: {
            opt1: 'multipart/form-data',
            opt2: 'application/x-www-form-urlencoded',
            opt3: 'text/plain',
            opt4: 'application/json'
        }
    },
    form: {
        enter_name: 'Enter the name',
        enter_value: 'Enter the value',
        enter_description: 'Enter the description',
        new_field: 'New Field',
        options_list: 'Options for the list',
        sig_digits: 'Significant digits',
        field: {
            type: {
                text: 'Text',
                date: 'Date',
                list: 'List',
                text_box: 'Text box',
                numero: 'Number',
                dynamic_list: 'Dynamic List'
            },
            numero_type: {
                entero_type: 'Integer',
                decimal_type: 'Decimal'
            }
        },
        validations: {
            required_name: 'Required name',
            required_description: 'Required description',
            not_empty_list: 'The list cannot be empty',
            field_already_in_form: 'The field already exists in the form',
            option_already_in_list: 'The option is already on the list',
            not_empty_form_field:
                'There must be at least one field in the form',
            repeated_form_name: 'There is already a form with that name'
        }
    },
    pause: {
        enter_name: 'Enter the name',
        edit_pause: 'Edit pause',
        new_pause: 'New pause',
        validations: {
            repeated_pause_name: 'There is already a pause with that name'
        },
        types: {
            opt1: 'Productive',
            opt2: 'Recreational'
        }
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
            agent: 'Agent',
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
        on_row_reorder:
            'Reordered routes, to finalize the change execute the reorder action',
        validations: {
            not_empty_dial_patterns: 'There must be at least one dial pattern',
            not_empty_trunks: 'There must be at least one trunk',
            repeated_route_name: 'Outgoing route with that name already exists',
            invalid_route_name: 'The path name is invalid',
            repeated_dial_pattern_prefix:
                'There is already a dial pattern with that prefix',
            repeated_dial_pattern_rule:
                'There is already a dial pattern with that rule',
            trunk_already_exists: 'Trunk already exists',
            orphan_trunks:
                'By eliminating the outgoing route the following Sip Trunks will remain unused by Outgoing routes'
        }
    },
    dial_pattern: {
        enter_pattern: 'Enter the pattern'
    },
    group_of_hour: {
        enter_name: 'Enter the name',
        validations: {
            not_empty_time_validations:
                'There must be at least one time validation',
            repeated_group_name: 'There is already a time group with that name',
            time_validation_already_exists:
                'The time validation already exists'
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
            invalid_campo_duracion:
                'If there is no duration, the duration field must exist.',
            invalid_name_campo_token: 'The token field name is invalid',
            invalid_name_campo_duracion: 'The duration field name is invalid'
        }
    },
    ivr: {
        enter_name: 'Enter the name',
        enter_description: 'Enter the description',
        validations: {
            not_empty_time_validations:
                'There must be at least one time validation',
            repeated_ivr_name: 'IVR with that name already exists',
            destination_option_already_exists:
                'Destination option already exists'
        },
        destination_types: {
            campaign: 'Inbound campaign',
            validation_date: 'Date/time validation',
            ivr: 'IVR',
            hangup: 'Hang Up',
            id_client: 'Client identifier',
            custom_dst: 'Custom destination',
            agent: 'Agent'
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
            repeated_dtmf:
                'There is already a destination option with that DTMF',
            invalid_dtmf:
                'The DTMF value must have a maximum five digit (0-9) or character (#, -, *)'
        }
    },
    register_server: {
        enter_name: 'Enter the name or company',
        enter_password: 'Enter the password',
        enter_email: 'Enter the email',
        enter_phone: 'Example: 5555555555',
        validations: {
            forbidden:
                'You do not have permissions to register the instance. Please contact your Administrator'
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
                text: 'Text',
                image: 'Image',
                file: 'File',
                audio: 'Audio',
                video: 'Video',
                sticker: 'Sticker',
                location: 'Location',
                contact: 'Contact'
            },
            fields: {
                text: 'Text',
                url: 'Url',
                preview_url: 'Preview URL',
                caption: 'Caption',
                filename: 'Filename',
                longitude: 'Longitude',
                latitude: 'Latitude',
                name: 'Name',
                address: 'Address'
            },
            help_text: {
                audio: {
                    url: 'Public URL of the audio file'
                },
                image: {
                    original_url: 'Public URL of the image hosted',
                    preview_url: 'Public URL of the thumbnail of the image',
                    caption: 'Caption of the image'
                },
                file: {
                    url: 'Public URL of the file hosted',
                    filename: 'Name of the file'
                },
                video: {
                    url: 'Public URL of the video file',
                    caption: 'Caption of the video'
                },
                sticker: {
                    url: 'Public URL of the sticker file'
                }
            }
        },
        line: {
            validations: {
                field_is_required: '{field} is required',
                max_len: 'Ensure this field has no more than {max_len} characters.',
                whatsapp_habilitado: 'This campaign does not have the channel enabled, activation will be forced.',
                max_len_help: 'This field only supports {max_len} characters.',
            },
            destination_types: {
                campaign: 'Campaign',
                menu: 'Interactive Menu'
            },
            options: {
                success_create: 'Destination option created successfully',
                success_update: 'Destination option updated successfully',
                success_delete: 'Destination option successfully removed',
                empty_options: 'No destination options configured'
            },
            only_whatsapp_habilitado: 'Only campaigns with the channel enabled'
        },
        group_of_message_template: {
            validations: {
                not_empty_templates: 'There must be at least one template'
            }
        },
        group_of_whatsapp_template: {
            validations: {
                not_empty_templates: 'There must be at least one template'
            }
        },
        contact: {
            validations: {
                field_is_required: '{field} is required',
                invalid_field: '{field} has an invalid format'
            }
        },
        disposition_chat: {
            validations: {
                field_is_required: '{field} is required'
            },
            form_types: {
                management: 'Gestion',
                schedule: 'Schedule',
                no_action: 'No action'
            },
            field_types: {
                text: 'Text',
                date: 'Date',
                list: 'List',
                text_box: 'Text box',
                numero: 'Number'
            }
        },
        reports: {
            general: {
                form_filters: {
                    start_date: 'Start date',
                    end_date: 'Ending date'
                },
                validations: {
                    biggest_start_data:
                        'The start date cannot be greater than the end date',
                    campaign_required: 'Campaign is required'
                }
            },
            campaign: {
                conversation: {
                    form_filters: {
                        start_date: 'Start date',
                        end_date: 'Ending date',
                        phone: 'Phone',
                        agent: 'Agent',
                        placeholders: {
                            start_date: 'Select the date',
                            end_date: 'Select the date',
                            phone: 'Enter the phone',
                            agent: 'Select agents',
                            without_agent: 'No agent'
                        }
                    },
                    validations: {
                        biggest_start_data:
                            'The start date cannot be greater than the end date'
                    }
                }
            }
        },
        conversation: {
            new: {
                validations: {
                    search_contact: {
                        empty_campaign: 'You must select a campaign to search for contacts'
                    }
                }
            }
        }
    }
};
