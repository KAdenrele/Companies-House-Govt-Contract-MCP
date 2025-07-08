#!/bin/sh
pip3 install "mcp[cli]" pandas pyarrow  fastmcp "uvicorn[standard]" 
pip install --upgrade certifi
pip3 install pytesseract opencv-python pdf2image
pip3 install langchain langchain-community langchain_google_genai faiss-cpu unstructured pi_heif unstructured_inference pytesseract "unstructured[pdf]" ipywidgets
