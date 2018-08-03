CREATE OR REPLACE FUNCTION insert_queue_log_ominicontacto_queue_log() returns trigger as $$import datetime
from plpy import spiexceptions

# TODO: refactorizar este código despues del volumen de código añadido con los nuevos eventos
# de transferencias

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
    'NONDIALPLAN',
    'CONGESTION',
]

EVENTOS_TRANSFERENCIAS = [
    'BT-TRY',
    'BT-ANSWER',
    'BT-BUSY',
    'BT-CANCEL',
    'BT-CHANUNAVAIL',
    'BT-CONGESTION',
    'BT-ABANDON',
    'CAMPT-TRY',
    'CAMPT-FAIL',
    'CAMPT-COMPLETE',
    'ENTERQUEUE-TRANSFER',
    'CT-TRY',
    'CT-ANSWER',
    'CT-ACCEPT',
    'CT-COMPLETE',
    'CT-DISCARD',
    'CT-BUSY',
    'CT-CANCEL',
    'CT-CHANUNAVAIL',
    'CT-CONGESTION',
    'BTOUT-TRY',
    'BTOUT-ANSWER',
    'BTOUT-BUSY',
    'BTOUT-CANCEL',
    'BTOUT-CONGESTION',
    'BTOUT-CHANUNAVAIL',
    'BTOUT-ABANDON',
    'CTOUT-TRY',
    'CTOUT-ANSWER',
    'CTOUT-ACCEPT',
    'CTOUT-COMPLETE',
    'CTOUT-DISCARD',
    'CTOUT-BUSY',
    'CTOUT-CANCEL',
    'CTOUT-CHANUNAVAIL',
    'CTOUT-CONGESTION',
    'COMPLETE-CTOUT',
    'COMPLETE-CT',
    'COMPLETE-BT',
    'COMPLETE-BTOUT',
    'COMPLETE-CAMPT',
]

EVENTOS = EVENTOS_LLAMADAS + EVENTOS_TRANSFERENCIAS


def procesar_datos_transferencias():
    """Parsea la información de los valores generados desde los campos 'agent', 'data4' y
    'data5' para obtener los valores de los campos de los logs de transferencias de llamadas:
    (agente_extra_id, campana_extra_id, numero_extra)
    """
    agente_data = TD['new']['agent']
    agente_id_modificado, agente_extra_id, campana_extra_id, numero_extra = (-1,) * 4
    try:
        valor_transf_1, valor_transf_2 = agente_data.split("-")
    except ValueError:
        valor_transf_1, valor_transf_2 = agente_data, None
    if event in ['BT-TRY', 'CAMPT-COMPLETE', 'CT-TRY']:
        # agente_id_origen - id_agente_origen
        agente_id_modificado = valor_transf_1
        agente_extra_id = valor_transf_2
    elif event == 'CAMPT-TRY':
        # agente_id - id_camp_destino
        agente_id_modificado = valor_transf_1
        campana_extra_id = valor_transf_2
    elif event == 'ENTERQUEUE-TRANSFER':
        # id_camp_origen - id_agente_origen (en data4, data5)
        campana_extra_id = TD['new']['data4']
        agente_id_modificado = TD['new']['data5']
    elif event in ['BTOUT-TRY', 'CTOUT-TRY']:
        # agente_id_origen - nro_telefono_destino
        agente_id = valor_transf_1
        numero_extra = valor_transf_2
    elif event in ['BTOUT-ANSWER', 'BTOUT-BUSY', 'BTOUT-CANCEL', 'BTOUT-CONGESTION',
                   'BTOUT-CHANUNAVAIL', 'CTOUT-ANSWER', 'CTOUT-ACCEPT', 'CTOUT-DISCARD',
                   'CTOUT-BUSY', 'CTOUT-CANCEL', 'CTOUT-CHANUNAVAIL', 'CTOUT-CONGESTION',
                   'COMPLETE-BTOUT', 'COMPLETE-CTOUT']:
        # el valor del campo 'agent' tiene un número de telefono
        agente_id_modificado = -1
        numero_extra = valor_transf_1
    else:
        # en los eventos de transferencias con un solo valor que contiene el id de un agente
        # solo se mantiene el valor de 'agente_id'
        agente_id_modificado = valor_transf_1
    return agente_id_modificado, agente_extra_id, campana_extra_id, numero_extra


if event in EVENTOS_AGENTE and queuename == 'ALL':
    # es un log de la actividad de un agente
    plan_agente_log = plpy.prepare(
        "INSERT INTO reportes_app_actividadagentelog(time, agente_id, event, pausa_id) VALUES($1 ,$2, $3, $4)",
        ["timestamp with time zone", "int", "text", "text"])
    plpy.execute(plan_agente_log, [fecha, agente_id, event, data1])
elif event in EVENTOS:
    # es un log que forma parte de una llamada
    try:
        campana_id, tipo_campana, tipo_llamada = queuename.split("-")
    except ValueError:
        campana_id, tipo_campana, tipo_llamada = (-1, -1, -1)

    if event in EVENTOS_TRANSFERENCIAS:
        (agente_id, agente_extra_id, campana_extra_id,
         numero_extra) = procesar_datos_transferencias()
    else:
        agente_extra_id, campana_extra_id, numero_extra = (-1, -1, -1)
    plan_llamadas_log = plpy.prepare(
        "INSERT INTO reportes_app_llamadalog(time, callid, campana_id, tipo_campana, tipo_llamada, agente_id, event, numero_marcado, contacto_id, bridge_wait_time, duracion_llamada, archivo_grabacion, agente_extra_id, campana_extra_id, numero_extra) VALUES($1 ,$2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)",
        ["timestamp with time zone", "text", "int", "int", "int", "int", "text", "text", "int",
         "int", "int", "text", "int", "int", "text"])
    plpy.execute(plan_llamadas_log, [fecha, callid, campana_id, tipo_campana, tipo_llamada,
                                     agente_id, event, data1, contacto_id, bridge_wait_time,
                                     duracion_llamada, archivo_grabacion, agente_extra_id,
                                     campana_extra_id, numero_extra])
else:
    # no insertamos logs de estos eventos de momento
    pass

$$ language plpythonu;
