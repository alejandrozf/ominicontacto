
def process_event(x):
    POSICION_ID_EN_CLAVE_REDIS = 10
    agent_id = x['key'][POSICION_ID_EN_CLAVE_REDIS:]
    value = x['value']
    streams = value['STREAMS'].split(',') if value['STREAMS'] else []
    for stream in streams:
        if execute('exists', stream) == 1:
            value['id'] = agent_id
            execute('XADD', stream, 'MAXLEN', '~', 100, '*', 'value', value)


GearsBuilder(desc='sup_agent') \
    .map(process_event) \
    .register('OML:AGENT:*', keyTypes=['hash'])
