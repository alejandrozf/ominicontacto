#!/bin/bash

source "$(pwd)"/.env

EXEC_POSTGRES="docker exec -i oml-postgresql-prodenv bash -c"

$EXEC_POSTGRES "PGUSER=$PGUSER psql -c \"ALTER USER $PGUSER WITH PASSWORD '$PGPASSWORD';\""
