from utils.mcp_instance import mcp
from utils.companies_house_API import get_companies_information

@mcp.tool(name="get_company_profile")
def get_company_profile(companyNumber:str) -> str:
    """
    Obtain the profile of a company from companies house.
    Args:
       - companyNumber
    Returns:
        status code - an integer which which corresponds to the status of an API call. 200 = success, 401 = unauthorised, 404 = resource not found.
        Resonse in JSON format, company profile information.
    """

    response = get_companies_information(path_param=companyNumber)
    return response.status_code, response.json()

