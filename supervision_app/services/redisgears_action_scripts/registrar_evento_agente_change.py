
def process_event(x):
    value = x['value']
    try:
        streams = value['STREAMS'].split(',')
    except:
        streams = []
    for stream in streams:
        if execute('exists', stream) == 1:
            execute('XADD', stream, 'MAXLEN', '~', 100, '*', 'value', value)


GearsBuilder(desc='sup_agent') \
    .foreach(process_event) \
    .register('OML:AGENT:*', keyTypes=['hash'], mode='sync')
