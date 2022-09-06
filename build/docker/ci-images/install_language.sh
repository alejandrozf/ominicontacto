#!/bin/bash
PGUSER=$POSTGRES_USER psql -d template1 -c "CREATE EXTENSION plperl"
