CREATE TRIGGER trigger_queue_log
AFTER INSERT
ON queue_log
FOR EACH ROW
EXECUTE PROCEDURE insert_queue_log_ominicontacto_queue_log();