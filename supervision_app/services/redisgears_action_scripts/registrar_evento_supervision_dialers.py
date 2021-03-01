def process_event(x):
    POSICION_ID_EN_CLAVE_REDIS = 23  # len('OML:SUPERVISION_DIALER:')
    value = x['value']
    if value is not None:
        campaign_id = x['key'][POSICION_ID_EN_CLAVE_REDIS:]
        streams = []
        try:
            data_redis_key = 'OML:SUPERVISION_DIALER_STREAMS:' + campaign_id
            streams = execute('HGET', data_redis_key, 'STREAMS')  # noqa: F821
            streams = streams.split(',')
        except:  # noqa: E722
            pass
        for stream in streams:
            if execute('exists', stream) == 1 and value is not None:  # noqa: F821
                value['id'] = campaign_id
                execute('XADD', stream, 'MAXLEN', '~', 20, '*', 'value', value)  # noqa: F821


GearsBuilder(desc='sup_dialers').map(process_event).register('%s', keyTypes=['hash'])  # noqa: F821
