create function insert_queue_log_ominicontacto_queue_log() returns trigger as $$
import datetime
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
plan = plpy.prepare("INSERT INTO ominicontacto_app_queuelog(time, callid, queuename, agent, event, data1, data2, data3, data4, data5) VALUES($1 ,$2, $3, $4, $5, $6, $7, $8, $9, $10)", ["timestamp with time zone", "text", "text", "text", "text", "text", "text", "text", "text", "text"])
plpy.execute(plan, [fecha, callid, queuename, agent, event, data1, data2, data3, data4, data5])
$$ language plpythonu;