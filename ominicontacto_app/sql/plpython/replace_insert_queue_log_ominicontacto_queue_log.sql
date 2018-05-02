CREATE OR REPLACE FUNCTION insert_queue_log_ominicontacto_queue_log() returns trigger as $$import datetime
from plpy import spiexceptions

tiempo = TD['new']['time']
fecha = datetime.datetime.strptime(tiempo, '%Y-%m-%d %H:%M:%S.%f')
callid = TD['new']['callid']
queuename = TD['new']['queuename']  # <id-campana>-<tipo-campana>-<tipo-llamada>
agente_id = TD['new']['agent']
event = TD['new']['event']
# 'data1' en los logs de llamadas tiene el número marcado y en los eventos de agente
# el id de la pausa
data1 = TD['new']['data1']
contacto_id = TD['new']['data2']
bridge_wait_time = TD['new']['data3']
duracion_llamada = TD['new']['data4']
archivo_grabacion = TD['new']['data5']

EVENTOS_AGENTE = ['ADDMEMBER', 'REMOVEMEMBER', 'PAUSEALL', 'UNPAUSEALL']

EVENTOS_LLAMADAS = [
    'DIAL',
    'ANSWER',
    'CONNECT',
    'COMPLETEAGENT',
    'COMPLETECALLER',
    'ENTERQUEUE',
    'EXITWITHTIMEOUT',
    'ABANDON',
    'NOANSWER',
    'CANCEL',
    'BUSY',
    'CHANUNAVAIL',
    'OTHER',
    'FAIL',
    'AMD',
    'BLACKLIST',
    'RINGNOANSWER',
]


if event in EVENTOS_AGENTE and queuename == 'ALL':
    # es un log de la actividad de un agente
    plan_agente_log = plpy.prepare(
        "INSERT INTO reportes_app_actividadagentelog(time, agente_id, event, pausa_id) VALUES($1 ,$2, $3, $4)",
        ["timestamp with time zone", "int", "text", "text"])
    plpy.execute(plan_agente_log, [fecha, agente_id, event, data1])
elif event in EVENTOS_LLAMADAS:
    # es un log que forma parte de una llamada
    try:
        campana_id, tipo_campana, tipo_llamada = queuename.split("-")
    except ValueError:
        campana_id, tipo_campana, tipo_llamada = (-1, -1, -1)

    if agente_id == 'dialer-dialout':
        agente_id = -1

    plan_llamadas_log = plpy.prepare(
        "INSERT INTO reportes_app_llamadalog(time, callid, campana_id, tipo_campana, tipo_llamada, agente_id, event, numero_marcado, contacto_id, bridge_wait_time, duracion_llamada, archivo_grabacion) VALUES($1 ,$2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)",
        ["timestamp with time zone", "text", "int", "int", "int", "int", "text", "text", "int",
         "int", "int", "text"])
    plpy.execute(plan_llamadas_log, [fecha, callid, campana_id, tipo_campana, tipo_llamada,
                                     agente_id, event, data1, contacto_id, bridge_wait_time,
                                     duracion_llamada, archivo_grabacion])
else:
    # no insertamos logs de estos eventos de momento
    pass

$$ language plpythonu;
