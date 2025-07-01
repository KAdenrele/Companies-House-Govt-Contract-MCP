import httpx
import asyncio
import os
import tomllib
import logging
from dotenv import load_dotenv
load_dotenv()

with open("config.toml", "rb") as f:
    config = tomllib.load(f)


class companies_house:
    def __init__(self,  api_key  = os.getenv("COMPANIES_HOUSE_API_KEY") , host_api: str = "https://api.companieshouse.gov.uk"):
        if not api_key:
            raise ValueError("API key cannot be empty or None.")
        self.api_key = api_key
        self.host_api = config["companies_house"]["api_host"]
        self.competitors = config['competitors']
        self.auth = (self.api_key, "")

    async def get_company_information_async(self, company_number:str, purpose:str, query_params:dict ={}):
        """
        Asynchronously fetches company information from the Companies House API depending on the query parameter and purpose.
        """
        if purpose == "profile":
            url = f"{self.host_api}/company/{company_number}"
        elif purpose == "officers":
            url = f"{self.host_api}/company/{company_number}/{purpose}"
        elif purpose == "persons-with-significant-control":
            url = url = f"{self.host_api}/company/{company_number}/{purpose}"
        elif purpose == "filing-history":
            url = url = f"{self.host_api}/company/{company_number}/{purpose}"
        else:
            #Just get profile from companies house if any issues.
            url = f"{self.host_api}/company/{company_number}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url= url, auth=self.auth, params=query_params)
            return response
        
    
    async def get_company_latest_filing_async(self, company_number:str, query_params:dict= {
                                                                                            "category": "accounts", 
                                                                                            "items_per_page":1
                                                                                            } 
                                                                                                ):
        """
        Asynchronously fetches latest company filing.
        """

        async with httpx.AsyncClient() as client:
            response = await self.get_company_information_async(company_number=company_number, purpose="filing-history", query_params= query_params)
            return response
    
    async def get_document_metadata_url(self, response):
        """
       Takes a single json of company filing history and extracts the document metadata.
        """
        document_metadata_url = response.json()['items'][0]['links']['document_metadata']

        return document_metadata_url
    
    async def get_document_metadata(self, document_metadata_url:str):
        """
        Downloads filing document.
        """

        async with httpx.AsyncClient() as client:
            document_metadata_response = await client.get(url= document_metadata_url, auth=self.auth)
            return document_metadata_response
    
    async def get_download_document(self, document_metadata_response):
        """
        Downloads filing document.
        """
        metadata_dict = document_metadata_response.json()
        document_url =metadata_dict['links']['document']

        content_type = str(list(metadata_dict['resources'].keys())[0])
        headers = {
            "Accept": content_type
        }


        if content_type == 'application/pdf':
             file_extension = '.pdf'
        else:
            file_extension = ""
            print("extension not accounted for")

        file_name = f"{metadata_dict["company_number"]}{metadata_dict['barcode']}{metadata_dict['category']}{file_extension}"
        
        
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                document_response = await client.get(url=document_url, auth=self.auth, headers=headers)


                document_response.raise_for_status() 

                with open(file=file_name, mode="wb") as f:
                    f.write(document_response.content)

                print(f"Successfully downloaded: {file_name}")
                return document_response.status_code # Will be 200-299 if raise_for_status passes

            except httpx.HTTPStatusError as e:
                print(f"HTTP Error during download: {e.response.status_code} - {e.response.text}")
                return e.response.status_code # Return the error status code

            except httpx.RequestError as e:
                print(f"Request Error during download ({e.request.url}): {e}")
                return None # Indicate a request/network failure

            except Exception as e:
                print(f"An unexpected error occurred during download: {e}")
                return None # Catch any other unforeseen issues
            

    async def get_document_with_company_number_async(self, company_number: str):
        """
        Downloads the latest filing document using the company_number.
        Returns the downloaded document content or None if an error occurs.
        """
        try:
            # Step 1: Get the latest filing information
            logging.info(f"Fetching latest filing for company number: {company_number}")
            company_filings = await self.get_company_latest_filing_async(company_number=company_number)
            if not company_filings:
                logging.warning(f"No filings found for company number: {company_number}")
                return None

            # Step 2: Extract the document metadata URL
            metadata_url = await self.get_document_metadata_url(response=company_filings)
            if not metadata_url:
                logging.error("Could not extract document metadata URL from the filing response.")
                return None

            # Step 3: Get the document metadata
            logging.info(f"Fetching document metadata from: {metadata_url}")
            document_metadata = await self.get_document_metadata(document_metadata_url=metadata_url)
            if not document_metadata:
                logging.error("Failed to retrieve document metadata.")
                return None

            # Step 4: Download the document
            logging.info("Downloading document.")
            download = await self.get_download_document(document_metadata_response=document_metadata)
            
            logging.info(f"Successfully downloaded document for company: {company_number}")
            return download

        except httpx.HTTPStatusError as e:
            # Specific handling for HTTP errors (e.g., 404 Not Found, 429 Rate Limit)
            logging.error(f"HTTP error for company {company_number}: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            # General exception handler for other issues (e.g., network errors, parsing errors)
            logging.error(f"An unexpected error occurred for company {company_number}: {e}", exc_info=True)
            return None


test = asyncio.run(companies_house().get_document_with_company_number_async(company_number="06440931"))

