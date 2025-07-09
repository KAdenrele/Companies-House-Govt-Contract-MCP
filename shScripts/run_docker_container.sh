#!/bin/sh
# Then, run it and map the ports
# Format is -p <host_port>:<container_port>. ./ = from current directory.
docker run -p 50000:50000 --env-file ./.env my-mcp-server-app