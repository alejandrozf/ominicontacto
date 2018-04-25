CREATE OR REPLACE FUNCTION insert_queue_log_ominicontacto_queue_log() returns trigger as $$import datetime
from plpy import spiexceptions

types_keys = ("IN", "DIALER", "saliente", "preview")
types_values = range(1, 5)

tiempo = TD['new']['time']
fecha = datetime.datetime.strptime(tiempo, '%Y-%m-%d %H:%M:%S.%f')
callid = TD['new']['callid']
queuename = TD['new']['queuename']  # <id-campana>-<tipo-campana>-<tipo-llamada>
agente_id = TD['new']['agent']
event = TD['new']['event']
numero_marcado = TD['new']['data1']
contacto_id = TD['new']['data2']
# el campo 'data3' no lo usamos por el momento
tiempo_ring = TD['new']['data4']
duracion_llamada = TD['new']['data5']

EVENTOS_AGENTE = ['ADDMEMBER', 'REMOVEMEMBER']

EVENTOS_NO_INSERTAR = [
    'PAUSE',
    'UNPAUSE',
    'CONFIG_RELOAD',
    'CALLSTATUS',
    'CALLOUTBOUND',
    'INFO',
    'QUEUESTART',
    'CONFIGRELOAD',
    'COMPLETECALL',
    'PAUSE',
    'UNPAUSE',
]

try:
    campana_id, tipo_campana, tipo_llamada = queuename.split("-")
except ValueError:
    campana_id, tipo_campana, tipo_llamada = (-1, -1, -1)


if event in EVENTOS_AGENTE and queuename == 'ALL':
    # es un log de la actividad de un agente
    plan_agente_log = plpy.prepare(
        "INSERT INTO reportes_actividadagentelog(time, agente_id, event, pausa_id) VALUES($1 ,$2, $3, $4)",
        ["timestamp with time zone", "int", "text", "text"])
    plpy.execute(plan_agente_log, [fecha, agente_id, event, data1])
elif event in EVENTOS_NO_INSERTAR:
    # no insertamos logs de estos eventos
    pass
else:
    # es un log que forma parte de una llamada
    plan_llamadas_log = plpy.prepare(
        "INSERT INTO reportes_llamadaslog(time, callid, campana_id, tipo_campana, tipo_llamada, agente_id, event, numero_marcado, contacto_id, tiempo_ring, tiempo_llamada) VALUES($1 ,$2, $3, $4, $5, $6, $7, $8, $9, $10, $11)",
        ["timestamp with time zone", "text", "int", "int", "int", "int", "text", "text", "text",
         "text", "text"])
    plpy.execute(plan_llamadas_log, [fecha, callid, campana_id, tipo_campana, tipo_llamada,
                                     agente_id, event, numero_marcado, contacto_id, tiempo_ring,
                                     duracion_llamada])

$$ language plpythonu;
