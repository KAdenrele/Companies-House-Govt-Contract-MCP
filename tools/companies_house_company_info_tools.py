from utils.mcp_instance import mcp
from utils.companies_house_API import get_companies_information_async

@mcp.tool(name="get_company_profile")
async def get_company_profile(company_number: str) -> dict: 
    """
    Obtains the profile of a company from Companies House.

    Args:
        company_number (str): The official registration number for the company.

    Returns:
        dict: A dictionary containing the API response. On success, it's the company profile. On failure, it contains error details.
    """
 
    response = await get_companies_information_async(path_param=company_number)


    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {
            "status": "error",
            "statusCode": response.status_code,
            "details": response.text  # .text is often more informative for errors than .json()
        }