CREATE OR REPLACE FUNCTION insert_queue_log_ominicontacto_queue_log() returns trigger as $$import datetime
from plpy import spiexceptions

types_keys = ("IN", "DIALER", "saliente", "preview")
types_values = range(1, 5)

tiempo = TD['new']['time']
fecha = datetime.datetime.strptime(tiempo, '%Y-%m-%d %H:%M:%S.%f')
callid = TD['new']['callid']
queuename = TD['new']['queuename']
agent = TD['new']['agent']
event = TD['new']['event']
data1 = TD['new']['data1']
data2 = TD['new']['data2']
data3 = TD['new']['data3']
data4 = TD['new']['data4']
data5 = TD['new']['data5']

campana = queuename.split('_')
try:
    campana_id = int(campana[0])
except ValueError:
    campana_id = -1
agente = agent.split('_')
try:
    agente_id = int(agente[0])
except ValueError:
    agente_id = -1

plan_llamadas_log = plpy.prepare(
    "INSERT INTO reportes_llamadaslog(time, callid, campana_id, agente_id, event, data1, data2, data3, data4, data5) VALUES($1 ,$2, $3, $4, $5, $6, $7, $8, $9, $10)",
    ["timestamp with time zone", "text", "int", "int", "text", "text", "text", "text", "text",
     "text"])
plan_agente_log = plpy.prepare(
    "INSERT INTO reportes_actividadagentelog(time, agente_id, event, data1) VALUES($1 ,$2, $3, $4)",
    ["timestamp with time zone", "int", "text", "text"])


if event in ['ADDMEMBER', 'REMOVEMEMBER']:
    # es un log de la actividad de un agente
    plpy.execute(plan_agente_log, [fecha, agente_id, event, data1])
elif event in ['PAUSEALL', 'UNPAUSEALL']:
    # no insertamos logs de estos eventos
    pass
else:
    # es un log que forma parte de una llamada
    plpy.execute(plan_llamadas_log, [fecha, callid, campana_id, agente_id, event, data1, data2,
                                     data3, data4, data5])

$$ language plpythonu;
