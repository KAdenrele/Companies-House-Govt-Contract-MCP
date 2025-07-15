#!/bin/sh
# -p <host_port>:<container_port>. 
docker run -p 50000:50000 --env-file ./.env my-mcp-server-app