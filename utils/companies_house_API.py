import httpx
import os
import tomllib
from dotenv import load_dotenv
load_dotenv()

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

companies_house_api_host = config["companies_house"]["api_host"]
COMPANIES_HOUSE_API_KEY = os.getenv("COMPANIES_HOUSE_API_KEY")

async def get_companies_information_async(path_param, **query_params):
    """
    Asynchronously fetches company information from the Companies House API.
    """
    url = f"{companies_house_api_host}/company/{path_param}"
    auth = (COMPANIES_HOUSE_API_KEY, "")

    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, auth=auth, params=query_params)
        return response
