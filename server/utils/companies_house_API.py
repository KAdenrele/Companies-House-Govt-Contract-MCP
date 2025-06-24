import requests 
import os
import tomllib
from dotenv import load_dotenv
load_dotenv()

with open("../config.toml", "rb") as f:
    config = tomllib.load(f)

companies_house_api_host = config["companies_house"]["api_host"]
COMPANIES_HOUSE_API_KEY = os.getenv("COMPANIES_HOUSE_API_KEY")

def get_companies_information(path_param, **query_params):
    """
    """
    url = f"{companies_house_api_host}/company/{path_param}"
    response = requests.get(url=url, auth=(COMPANIES_HOUSE_API_KEY, ""), params=query_params)
    return response


"""test_params = config["competitors"][0]["company_number"]
test_call = get_companies_information(path_param=test_params)
print(test_call.status_code)"""