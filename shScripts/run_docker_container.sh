#!/bin/sh
# -p <host_port>:<container_port>. 
# -v "$(pwd)/data:/app/data" for mounting files in the container
docker run -p 50000:50000 --env-file ./.env my-mcp-server-app