import json


def prepara_sup_entrantes_para_stream_redis(x):
    CAMPANAS_ID_LIST = '%s'.split(',')
    CAMPANAS_LIST = '%s'.split(',')
    POSICION_ID_EN_CLAVE_REDIS = 15
    supervisor_id = x['key'][POSICION_ID_EN_CLAVE_REDIS:]
    stream = f'supervisor_{supervisor_id}_%s'
    for i in range(0, len(CAMPANAS_ID_LIST)):
        camp_nombre = CAMPANAS_LIST[i]
        camp_id = CAMPANAS_ID_LIST[i]
        sup_camp_streams_key = 'OML:SUPERVISION_CAMPAIGN_STREAMS:' + camp_id
        sup_camp_streams = execute('HGET', sup_camp_streams_key, 'STREAMS')
        sup_camp_streams_list = sup_camp_streams.split(',') if sup_camp_streams else []
        if stream not in sup_camp_streams_list:
            sup_camp_streams_list.append(stream)
            execute('HSET', sup_camp_streams_key, 'STREAMS',
                    ','.join(sup_camp_streams_list))
        # para disparar el evento con el dato actual
        # que no tenga que esperar a la proxima ejecucion de cron
        sup_camp_key = f'OML:SUPERVISION_CAMPAIGN:{camp_id}'
        execute('HSET', sup_camp_key, 'START', 'True')
        if execute('exists', stream) == 0:
            execute('XADD', stream, '*', 'start', '{"value": "false"}')


GearsBuilder() \
    .map(prepara_sup_entrantes_para_stream_redis) \
    .run('OML:SUPERVISOR:%s')
