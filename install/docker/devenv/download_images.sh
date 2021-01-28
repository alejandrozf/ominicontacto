#!/bin/bash

echo "***[OML devenv] Pulling the latest images of services"
services=("acd" "app" "dialer" "kam" "nginx" "pgsql" "pbxemulator" "websockets")
for i in "${services[@]}"; do
  docker pull freetechsolutions/oml$i:develop
done
