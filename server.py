# server.py
from utils.mcp_instance import mcp
import os
from tools.csv_tools import summarize_csv_file 


#ßFastMCP decorated tools (e.g., summarize_csv_file) will automatically be registered

if __name__ == "__main__":
    print(f"Starting FastMCP server.")
    mcp.run()

    # For dev/debugging with the MCP Inspector:
    # mcp.dev()