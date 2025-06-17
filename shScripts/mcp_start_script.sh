#!/bin/sh
cd server
pip3 install "mcp[cli]" pandas pyarrow  fastmcp fastapi "uvicorn[standard]" fastapi-mcp #ensure you're using the .server_venv