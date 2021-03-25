
def process_event(x):
    STREAM_LENGHT = %d
    value = x['value']
    try:
        streams = value['STREAMS'].split(',')
    except:
        streams = []
    for stream in streams:
        if execute('exists', stream) == 1:
            execute('XADD', stream, 'MAXLEN', '~', STREAM_LENGHT, '*', 'value', value)


GearsBuilder(desc='sup_agent') \
    .foreach(process_event) \
    .register('OML:AGENT:*', keyTypes=['hash'], mode='sync')
