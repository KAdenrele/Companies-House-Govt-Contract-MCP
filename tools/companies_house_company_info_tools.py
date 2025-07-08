from utils.mcp_instance import mcp
from utils.companies_house_API import companies_house

@mcp.tool(name="list_available_competitors")
def get_competitors() -> dict:
    """
    Provides a list of competitors listed in the config.toml file to the user.

    Args:
        company_number (str): The official registration number for the company.

    Returns:
        dict: A dictionary containing a list of dictionaries like  {"competitor" :[{competitorone:{name:name, companynumber:12340}, "competitor" :[{competitortwo:{name:name2, companynumber:22567}]} of competitors and their details.
    """
    

    competitors = companies_house().competitors
    return competitors


@mcp.tool(name="get_company_profile")
async def get_company_profile(company_number: str) -> dict: 
    """
    Obtains the profile of a company from Companies House.

    Args:
        company_number (str): The official registration number for the company.

    Returns:
        dict: A dictionary containing the API response. On success, it's the company profile. On failure, it contains error details.
    """
    if company_number is None:
        return {
            "status": "user_guidance", 
            "message": "The company number is unknown. You should call the 'list_available_competitors' tool to get a list of companies and their numbers."
        }
 
    response = await companies_house().get_company_information_async(company_number=company_number)


    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {
            "status": "error",
            "statusCode": response.status_code,
            "details": response.text  # .text is often more informative for errors than .json()
        }
    
@mcp.tool(name="get_company_charges")
async def get_company_charges(company_number: str) -> dict: 
    """
    Obtains information relating to charges documented under a company from Companies House.

    Args:
        company_number (str): The official registration number for the company.

    Returns:
        dict: A dictionary containing the API response. On success, it's the company profile. On failure, it contains error details.
    """
    if company_number is None:
        return {
            "status": "user_guidance", 
            "message": "Ask user if you should call the 'list_available_competitors' tool to get a list of companies and their numbers."
        }
 
    response = await companies_house().get_company_information_async(company_number=company_number, purpose="charges")


    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {
            "status": "error",
            "statusCode": response.status_code,
            "details": response.text  # .text is often more informative for errors than .json()
        }
    

@mcp.tool(name="get_company_officers")
async def get_company_officers(company_number: str) -> dict: 
    """
    Obtains information about officers of a company from Companies House.

    Args:
        company_number (str): The official registration number for the company.

    Returns:
        dict: A dictionary containing the API response. On success, it's the listed officers. On failure, it contains error details.
    """
    
    if company_number is None:
        return {
            "status": "user_guidance", 
            "message": "The company number is unknown. You should call the 'list_available_competitors' tool to get a list of companies and their numbers."
        }
    response = await companies_house().get_company_information_async(company_number=company_number, purpose="officers")


    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {
            "status": "error",
            "statusCode": response.status_code,
            "details": response.text  # .text is often more informative for errors than .json()
        }
    

@mcp.tool(name="get_person_significant_control")
async def get_person_significant_control(company_number: str) -> dict: 
    """
    Obtains the details of persons with significant control ina. company.

    Args:
        company_number (str): The official registration number for the company.

    Returns:
        dict: A dictionary containing the API response. On success, it's the company profile. On failure, it contains error details.
    """
    if company_number is None:
        return {
            "status": "user_guidance", 
            "message": "The company number is unknown. You should call the 'list_available_competitors' tool to get a list of companies and their numbers."
        }
    
    response = await companies_house().get_company_information_async(company_number=company_number, purpose="persons-with-significant-control")


    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {
            "status": "error",
            "statusCode": response.status_code,
            "details": response.text  # .text is often more informative for errors than .json()
        }   
@mcp.tool(name="get_company_latest_filing")
async def get_company_latest_filing(company_number: str) -> dict: 
    """
    Obtains information about latest "account" type latest filing of a company from Companies House.

    Args:
        company_number (str): The official registration number for the company.

    Returns:
        dict: A dictionary containing the API response. On success, it's the company profile. On failure, it contains error details.
    """
    if company_number is None:
        return {
            "status": "user_guidance", 
            "message": "The company number is unknown. You should call the 'list_available_competitors' tool to get a list of companies and their numbers."
        }
 
    response = await companies_house().get_company_latest_filing_async(company_number=company_number)


    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {
            "status": "error",
            "statusCode": response.status_code,
            "details": response.text  # .text is often more informative for errors than .json()
        } 
    
@mcp.tool(name="search_by_sic_code")
async def get_company_by_sic(sic_codes: list[str], size: str = "10") -> dict: 
    """
    Searches for companies using the companies house API based on sic code

    Args:
        Sic code (str): 
        Size: Number of results to return.

    Returns:
        dict: A dictionary containing the API response. On success, it's the company profile. On failure, it contains error details.
    """
    if sic_codes is None:
        return {
            "status": "user_guidance", 
            "message": "Ask if user wantst to search for companies with the same sic code as Zaizi (62020)."
        }
 
    response = await companies_house().get_list_advanced_company_search(sic_codes=sic_codes, size=size )

    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {
            "status": "error",
            "statusCode": response.status_code,
            "details": response.text  
        } 
    