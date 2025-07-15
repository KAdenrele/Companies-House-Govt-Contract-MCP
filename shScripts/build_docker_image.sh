#!/bin/sh
#Build docker image
# --no-cache makes it a fresh build/rebuild... use/remove as required.
#docker build --no-cache -t my-mcp-server-app .
pip3 freeze > requirements.txt
docker build -t my-mcp-server-app .
