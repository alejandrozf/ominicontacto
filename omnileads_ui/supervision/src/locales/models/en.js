export default {
    agent_campaign: {
        name: 'Name',
        username: 'Username',
        sip: 'ID SIP',
        penalty: 'Penalty'
    },
    pause_set: {
        id: 'ID',
        name: 'Name'
    },
    pause_setting: {
        id: 'ID',
        pause: 'Pause',
        pause_type: 'Pause type',
        set: 'Set',
        time_to_end_pause: 'Time to end pause'
    },
    audit: {
        user: 'User',
        object: 'Object',
        name: 'Name',
        action: 'Action',
        additional_information: 'Additional Information',
        datetime: 'Datetime'
    },
    external_site: {
        id: 'ID',
        name: 'Name',
        url: 'Url',
        method: 'Method',
        format: 'Format',
        objective: 'Objective',
        trigger: 'Trigger',
        status: 'Status'
    },
    external_site_authentication: {
        id: 'ID',
        name: 'Name',
        url: 'Url',
        username: 'Username',
        password: 'Password',
        campo_token: 'Token field',
        duracion: 'Duration',
        campo_duracion: 'Duration field',
        token: 'Token',
        expiracion_token: 'Token expiration'
    },
    call_disposition: {
        id: 'ID',
        name: 'Name'
    },
    external_system: {
        id: 'ID',
        name: 'Name',
        agents: 'Agents'
    },
    agent_external_system: {
        id: 'ID',
        external_id: 'Id Externo Agente',
        agent: 'Agent'
    },
    form: {
        id: 'ID',
        name: 'Name',
        description: 'Description',
        fields: 'Fields',
        status: 'Status'
    },
    form_field: {
        id: 'ID',
        name: 'Name',
        order: 'Order',
        type: 'Type',
        required: 'Required?',
        list_options: 'List options'
    },
    pause: {
        id: 'ID',
        name: 'Name',
        type: 'Type',
        status: 'Active'
    },
    inbound_route: {
        id: 'ID',
        name: 'Name',
        phone: 'Number DID',
        caller_id: 'Caller Id',
        idiom: 'Idiom',
        destiny: 'Destiny',
        destiny_type: 'Destiny type'
    },
    outbound_route: {
        id: 'ID',
        name: 'Name',
        ring_time: 'Ring time',
        dial_options: 'Dial options',
        order: 'Order'
    },
    dial_pattern: {
        id: 'ID',
        prepend: 'Prepend',
        prefix: 'Prefix',
        pattern: 'Pattern',
        order: 'Order'
    },
    trunk: {
        id: 'ID',
        name: 'Name',
        order: 'Order'
    }
};
