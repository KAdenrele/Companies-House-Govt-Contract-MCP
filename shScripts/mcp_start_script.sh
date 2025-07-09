#!/bin/sh
pip3 install "mcp[cli]" pandas pyarrow  fastmcp "uvicorn[standard]" 
pip3 install pytesseract pdf2image 
pip3 install langchain_core langchain langchain_google_genai langchain_community faiss-cpu
