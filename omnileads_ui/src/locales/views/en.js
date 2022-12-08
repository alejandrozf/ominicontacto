export default {
    dashboard_home_page: {
        active_campaign_by_type: 'Active {type} Campaigns',
        agent_status: 'Agent Status',
        agent_status_oncall: 'On call',
        agent_status_pause: 'Pause',
        agent_status_ready: 'Ready',
        authenticated_agents: 'Authenticated Agents',
        califications: 'Dispositions',
        today: 'Today',
        yesterday: 'Yesterday',
        call_sumary: 'Call Sumary',
        call_sumary_attended: 'Attended',
        call_sumary_failed: 'Failed'
    },
    add_agents_to_campaign: {
        already_agent_in_campaign: 'The agent is already in the campaign',
        already_agents_in_campaign: 'The following agents were already in the campaign: ( {agents} ), therefore not added',
        empty_campaign_notice: 'The campaign will run out of agents',
        how_to_edit_penalty: 'To modify the penalty select the column',
        agents_campaign: 'Campaign agents',
        agents_not_save: 'Agents not saved'
    },
    pause_sets: {
        title: 'Pause sets',
        configured_pauses: 'Configured pauses',
        infinite_pause: 'Infinite pause',
        pause_settings_will_be_deleted: 'All pause settings will be removed',
        pause_sets_not_deleted: 'Pause set not removed',
        pause_config_not_deleted: 'Pause setting not removed',
        pause_sets_without_pauses: 'Cannot create a pause set without pauses',
        how_to_edit_pause_setting: 'To edit the pauses, click on the Time cell to end pause'
    },
    pause_setting: {
        max_time_allowed: 'The maximum pause time is 8 hours (28800 seconds)',
        min_time_allowed: 'Infinite time, it means that you will never leave the pause (0 seconds)'
    },
    audit: {
        title: 'Administrative audit'
    },
    external_sites: {
        list_title: 'External Sites',
        show_hiddens: 'Show hidden',
        remove_hiddens: 'Remove hidden',
        hide: 'Hide',
        show: 'Unhide'
    },
    external_site_authentication: {
        list_title: 'External site authentications',
        edit_title: 'Edit external site authentication',
        new_title: 'New external site authentication'
    },
    call_dispositions: {
        list_title: 'Call Dispositions',
        edit_title: 'Edit Call Disposition',
        new_title: 'New Call Disposition'
    },
    external_system: {
        new_agent_on_system: 'New agent in system',
        edit_agent_on_system: 'Edit agent in system'
    },
    form: {
        step1: {
            title: 'Form data'
        },
        step2: {
            title: 'Form fields'
        },
        step3: {
            title: 'Preview',
            display_name: 'Name:',
            display_description: 'Description:'
        }
    },
    outbound_route: {
        detail_title: 'Outbound route information',
        new_title: 'New Outbound route',
        edit_title: 'Edit Outbound route'
    },
    dial_pattern: {
        new_title: 'New dial pattern',
        edit_title: 'Edit dial pattern'
    },
    trunk: {
        new_title: 'New trunk',
        edit_title: 'Edit trunk'
    },
    group_of_hour: {
        new_title: 'New group of hour',
        edit_title: 'Edit group of hour'
    },
    time_validation: {
        new_title: 'New time validation',
        edit_title: 'Edit time validation'
    },
    ivr: {
        new_title: 'New IVR',
        edit_title: 'Edit IVR',
        configuration_time_out: 'Time Out Configuration',
        configuration_invalid_destination: 'Invalid destination Configuration',
        destinations: {
            time_out: 'Time out destination',
            invalid: 'Invalid destination'
        },
        audios: {
            types: {
                internal: 'Internal File',
                external: 'External File'
            },
            main: {
                title: 'Main audio',
                internal: 'Internal main audio',
                external: 'External main audio'
            },
            time_out: {
                title: 'Time out audio',
                internal: 'Internal time out audio',
                external: 'External time out audio'
            },
            invalid: {
                title: 'Invalid audio',
                internal: 'Internal invalid audio',
                external: 'External invalid audio'
            }
        }
    },
    destination_option: {
        new_title: 'New destination',
        edit_title: 'Edit destination'
    },
    register_server: {
        title: 'Instance record',
        info1: 'Thank you for using OMniLeads, the most complete and friendly Open Source Contact Center Suite on the market.',
        info2: 'Oops! This instance is not yet registered',
        info3: 'From this record, we can inform you about',
        info4: 'In addition, you can support us with use cases or software bugs in a more agile way (you can request to cancel the communication channel at any time',
        info5: 'In case of doubts, contact your Administrator',
        info6: 'New Releases',
        info7: 'New Addons',
        info8: 'Special offers',
        info9: 'Roadmap Trailers',
        info10: 'Blog Articles',
        info11: 'Product Notes',
        privacy_policies: 'Privacy policies',
        detail: {
            title: 'Thank you for your registration',
            already_register: 'Are you already registered',
            resend_key: 'Resend Key',
            user: 'User',
            http_responses: {
                res1: 'The key data was successfully sent to your email',
                res2: 'Failed to connect to the keyserver',
                res3: 'The data sent from the instance is not correct'
            }
        }
    },
    whatsapp: {
        message_template: {
            new_title: 'New message template',
            edit_title: 'Edit message template'
        },
        provider: {
            new_title: 'New provider',
            edit_title: 'Edit the provider'
        },
        line: {
            new_title: 'create whatsapp line',
            edit_title: 'edit whatsapp line',
            tipos_de_destino: {
                campana: 'Campaign',
                interactivo: 'Interactive'
            },
            step1: {
                title: 'Basic data'
            },
            step2: {
                title: 'Carrier data',
                sender: 'Sender',
                app_info: 'Info app'
            },
            step3: {
                title: 'Conection data',
                display_name: 'Name:',
                display_description: 'Description:',
                message: 'Messages',
                destination: 'Destination'
            }
        },
        group_of_message_template: {
            new_title: 'New group',
            edit_title: 'Edit group'
        }
    }
};
