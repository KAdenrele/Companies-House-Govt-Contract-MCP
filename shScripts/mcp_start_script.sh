#!/bin/sh
pip3 install "mcp[cli]" pandas pyarrow google-generativeai fastmcp
mkdir data tools utils
touch >> README.md server.py main.py
touch tools/csv_tools.py
touch tools/parquet_tools.py
echo "GEMINI_API_KEY=" >> .env
echo "id,name,email,signup_date
1,Alice Johnson,alice@example.com,2023-01-15
2,Bob Smith,bob@example.com,2023-02-22
3,Carol Lee,carol@example.com,2023-03-10
4,David Wu,david@example.com,2023-04-18
5,Eva Brown,eva@example.com,2023-05-30" >> data/sample.csv
