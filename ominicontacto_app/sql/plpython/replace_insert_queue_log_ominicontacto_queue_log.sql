CREATE OR REPLACE FUNCTION insert_queue_log_ominicontacto_queue_log() returns trigger as $$import datetime
from plpy import spiexceptions

types_keys = ("IN", "DIALER", "saliente", "preview")
types_values = range(1, 5)

tiempo = TD['new']['time']
fecha = datetime.datetime.strptime(tiempo, '%Y-%m-%d %H:%M:%S.%f')
callid = TD['new']['callid']
campana_id = TD['new']['queuename']
agente_id = TD['new']['agent']
event = TD['new']['event']
data1 = TD['new']['data1']      # numero marcado
data2 = TD['new']['data2']      # id contacto
data3 = TD['new']['data3']      # tipo llamada / tipo manual
data4 = TD['new']['data4']      # ring time
data5 = TD['new']['data5']      # duracion llamada

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

if event in EVENTOS_AGENTE and queuename == 'ALL':
    # es un log de la actividad de un agente
    plan_agente_log = plpy.prepare(
    "INSERT INTO reportes_actividadagentelog(time, agente_id, event, data1) VALUES($1 ,$2, $3, $4)",
    ["timestamp with time zone", "int", "text", "text"])
    plpy.execute(plan_agente_log, [fecha, agente_id, event, data1])
elif event in EVENTOS_NO_INSERTAR:
    # no insertamos logs de estos eventos
    pass
else:
    # es un log que forma parte de una llamada
    plan_llamadas_log = plpy.prepare(
    "INSERT INTO reportes_llamadaslog(time, callid, campana_id, agente_id, event, data1, data2, data3, data4, data5) VALUES($1 ,$2, $3, $4, $5, $6, $7, $8, $9, $10)",
    ["timestamp with time zone", "text", "int", "int", "text", "text", "text", "text", "text",
     "text"])
    plpy.execute(plan_llamadas_log, [fecha, callid, campana_id, agente_id, event, data1, data2,
                                     data3, data4, data5])

$$ language plpythonu;
