#!/bin/sh
python3 -m venv ./server/.server_venv
python3 -m venv ./frontend/.frontend_venv
source server/.server_venv/bin/activate # this needs to be run in the terminal manually and the same for frontend