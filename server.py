from tools.csv_tools import summarise_csv_file
import tools.companies_house_company_info_tools
import tools.knowledge_base_tools
from utils.mcp_instance import mcp


def main():
    print("Starting server")
    mcp.run(transport="streamable-http")
    



if __name__ == "__main__":
    main()