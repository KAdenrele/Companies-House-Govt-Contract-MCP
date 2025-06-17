from os import getenv
from utils.mcp_instance import mcp
from tools.csv_tools import summarise_csv_file 
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")