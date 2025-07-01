from utils.mcp_instance import mcp
from tools.csv_tools import summarise_csv_file
from tools.companies_house_company_info_tools import get_company_latest_filing, get_company_officers, get_company_profile, get_competitors, get_person_significant_control

if __name__ == "__main__":
    mcp.run(transport="streamable-http")