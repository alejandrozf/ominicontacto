CREATE TABLE queue_log (
id SERIAL PRIMARY KEY NOT NULL,
time varchar(26) default NULL,
callid varchar(32) NOT NULL default '',
queuename varchar(32) NOT NULL default '',
agent varchar(32) NOT NULL default '',
event varchar(32) NOT NULL default '',
data1 varchar(100) NOT NULL default '',
data2 varchar(100) NOT NULL default '',
data3 varchar(100) NOT NULL default '',
data4 varchar(100) NOT NULL default '',
data5 varchar(100) NOT NULL default '');
