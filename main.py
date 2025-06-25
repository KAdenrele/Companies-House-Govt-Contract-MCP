from utils.mcp_instance import mcp
from tools.csv_tools import summarise_csv_file
from tools.companies_house_company_info_tools import get_company_profile



if __name__ == "__main__":
    mcp.run(transport="streamable-http")