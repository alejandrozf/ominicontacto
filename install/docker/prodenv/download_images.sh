#!/bin/bash

echo "***[OML devenv] Pulling the latest images of services"
services=("acd" "app" "kam" "nginx" "websockets")
for i in "${services[@]}"; do
  docker pull freetechsolutions/oml$i:latest
done
