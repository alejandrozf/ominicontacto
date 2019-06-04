#!/bin/bash
CMD="createlang plpythonu"
PGUSER={{ postgres_user }} $CMD template1
PGUSER={{ postgres_user }} $CMD {{ postgres_database }}
PGUSER={{ postgres_user }} psql -c "GRANT ALL PRIVILEGES ON DATABASE {{ postgres_database }} TO {{ postgres_user }};"
PGUSER={{ postgres_user }} psql -c "ALTER USER {{ postgres_user }} WITH SUPERUSER;"
