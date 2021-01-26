import json


def prepara_agentes_para_stream_redis(x):
    POSICION_ID_EN_CLAVE_REDIS = 15
    supervisor_id = x['key'][POSICION_ID_EN_CLAVE_REDIS:]
    stream = f'supervisor_{supervisor_id}_agentes'
    for v in x['value'].keys():
        agent_key = f'OML:AGENT:{v}'
        if execute('exists', agent_key) == 1:
            agent_streams = execute('HGET', agent_key, 'STREAMS')
            agent_streams_list = agent_streams.split(',') if agent_streams else []
            if stream not in agent_streams_list:
                agent_streams_list.append(stream)
                execute('HSET', agent_key, 'STREAMS', ','.join(agent_streams_list))
            sup_value = json.loads(x['value'][v])
            agent_group = sup_value['grupo']
            execute('HSET', agent_key, 'GROUP', agent_group,
                    'CAMPANAS', sup_value['campana'])
        if execute('exists', stream) == 0:
            execute('XADD', stream, '*', 'start', '{"value": "false"}')


GearsBuilder() \
    .map(prepara_agentes_para_stream_redis) \
    .run('OML:SUPERVISOR:%s')
