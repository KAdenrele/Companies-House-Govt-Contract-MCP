import requests
import time
from datetime import date, timedelta, datetime
from typing import Optional, List, Dict, Any
import pandas as pd


BASE_URL = "https://www.contractsfinder.service.gov.uk"

def get_all_contracts(
    publishedFrom: Optional[str] = None, 
    publishedTo: Optional[str] = None, 
    stage: str = "awarded", 
    size: int = 100
) -> List[Dict[str, Any]]:
    
    # Start with the initial search URL
    next_url = f"{BASE_URL}/Published/Notices/OCDS/Search"
    
    all_results = []
    
    # Define the initial parameters, including 'size'
    params = {"stage": stage, "size": size}
    if publishedFrom: 
        params["publishedFrom"] = publishedFrom
    if publishedTo: 
        params["publishedTo"] = publishedTo
    
    # This flag ensures the initial 'params' are only used once
    is_first_request = True

    while next_url:
        try:
            # For the first request, send the parameters. 
            # For subsequent requests, the full URL provided by the API has everything it needs.
            if is_first_request:
                response = requests.get(next_url, params=params)
                is_first_request = False
            else:

                response = requests.get(next_url)

            response.raise_for_status()
            data = response.json()
            
            # Get the list of contracts from the 'releases' key
            releases_on_page = data.get("releases", [])
            all_results.extend(releases_on_page)
            

            # Get the 'links' dictionary, and then get the 'next' URL from inside it.
            # This is the correct way to get the URL for the next page.
            next_url = data.get('links', {}).get('next')
            
            # The loop will automatically stop when 'next_url' becomes None.
            
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            break # Stop on any network or HTTP error
            
    return all_results


def fetch_contracts_by_interval(start_date_str: str = "2025-01-01", day_interval: int = 1) -> List[Dict[str, Any]]:
    """
    Fetches all awarded contracts from a start date, in chunks of a given day interval.
    
    Args:
        start_date_str: The start date in "YYYY-MM-DD" format.
        day_interval: The number of days for each fetching interval (e.g., 7 for weekly).
    """
    try:
        current_interval_start = date.fromisoformat(start_date_str)
    except ValueError:
        print("Error: start_date_str must be in YYYY-MM-DD format.")
        return []

    today = date.today()
    all_contracts = []


    while current_interval_start <= today:

        interval_end_date = current_interval_start + timedelta(days=day_interval - 1)

        if interval_end_date > today:
            interval_end_date = today

        start_str_for_api = current_interval_start.strftime("%Y-%m-%d")
        end_str_for_api = interval_end_date.strftime("%Y-%m-%d")

        print(f"--- Fetching contracts for interval: {start_str_for_api} to {end_str_for_api} ---")
        contracts_in_interval = get_all_contracts(publishedFrom=start_str_for_api, publishedTo=end_str_for_api, stage="awarded")
        
        if contracts_in_interval:
            all_contracts.extend(contracts_in_interval)
            print(f"  ... found {len(contracts_in_interval)} contracts in this interval.")
        else:
            print("  ... found 0 contracts in this interval.")
        
        print(f"  Total contracts so far: {len(all_contracts)}\n")
        current_interval_start += timedelta(days=day_interval)
        
        time.sleep(1)

    print(f"Finished! A total of {len(all_contracts)} contracts were fetched.")
    return all_contracts

#-------------- Generating file---------
all_contracts_since_jan = fetch_contracts_by_interval(start_date_str = "2025-01-01", day_interval = 2)

contracts_df = pd.DataFrame(all_contracts_since_jan)

contracts_df = contracts_df.explode('awards').reset_index(drop=True)
contracts_df = contracts_df.explode('parties').reset_index(drop=True)
contracts_df['Tender ID'] = contracts_df['tender'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
contracts_df['Tender Title'] = contracts_df['tender'].apply(lambda x: x.get('title') if isinstance(x, dict) else None)
contracts_df['Party ID'] = contracts_df['parties'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
contracts_df['Party Name'] = contracts_df['parties'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
contracts_df['Buyer ID'] = contracts_df['buyer'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
contracts_df['Buyer Name'] = contracts_df['buyer'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)

contracts_df['Award ID'] = contracts_df['awards'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
contracts_df['Award Status'] = contracts_df['awards'].apply(lambda x: x.get('status') if isinstance(x, dict) else None)
contracts_df['Award Date'] = contracts_df['awards'].apply(lambda x: x.get('date') if isinstance(x, dict) else None)
contracts_df['Award Date Published'] = contracts_df['awards'].apply(lambda x: x.get('datePublished') if isinstance(x, dict) else None)
contracts_df['Award Value'] = contracts_df['awards'].apply(lambda x: x.get('value', {}).get('amount') if isinstance(x, dict) else None)
contracts_df['Award Currency'] = contracts_df['awards'].apply(lambda x: x.get('value', {}).get('currency') if isinstance(x, dict) else None)


contracts_df['Supplier ID'] = contracts_df['awards'].apply(lambda x: x.get('suppliers', [{}])[0].get('id') if isinstance(x, dict) else None)
contracts_df['Supplier Name'] = contracts_df['awards'].apply(lambda x: x.get('suppliers', [{}])[0].get('name') if isinstance(x, dict) else None)

contracts_df['Award Contract Start Date'] = contracts_df['awards'].apply(lambda x: x.get('contractPeriod', {}).get('startDate') if isinstance(x, dict) else None)
contracts_df['Award Contract End Date'] = contracts_df['awards'].apply(lambda x: x.get('contractPeriod', {}).get('endDate') if isinstance(x, dict) else None)
contracts_df = contracts_df.drop(columns=["awards", "tender", "parties", "buyer"])

contracts_df["Award Value"] = pd.to_numeric(contracts_df["Award Value"], errors="raise")
contracts_df["Award Date"] = pd.to_datetime(contracts_df["Award Date"], errors="raise", utc=True)
contracts_df['Award Year'] = contracts_df["Award Date"].dt.year
contracts_df['Award Month'] = contracts_df["Award Date"].dt.month
contracts_df['Award Day'] = contracts_df["Award Date"].dt.day
contracts_df["Award Contract Start Date"] = pd.to_datetime(contracts_df["Award Contract Start Date"], errors="raise", utc=True)
contracts_df["Award Contract End Date"] = pd.to_datetime(contracts_df["Award Contract End Date"], errors="raise", utc=True)

contracts_df["Award Date" ] = contracts_df["Award Date"].dt.strftime('%d-%m-%Y')
contracts_df[ "Award Contract Start Date"] = contracts_df["Award Contract Start Date"].dt.strftime('%d-%m-%Y')
contracts_df["Award Contract End Date" ] = contracts_df["Award Contract End Date" ].dt.strftime('%d-%m-%Y')

"""
old_column_names = contracts_df.columns
new_column_names = [
                    'Award ID','Award Status','Award Date','Data Award Published',
                    'Award Value', 'Award Value Currency',	
                    'Contracted Period Start Date',	'Contracted Period End Date',	
                    'Award Description','OCID', 'Contract ID','Language', 'date', 'tag', 'Initiation Type','Title', 'Planning', 'Related Processes', 'Tender ID',
                    'Tender Title','Party ID','Party Name', 'Buyer ID', 'Buyer Name', 'Supplier ID', 'Supplier Name',	'Award Document ID',
                    "Award Year", "Award Month", "Award Day"
                    ]

column_name_mapper = dict(zip(old_column_names,new_column_names))
contracts_df = contracts_df.rename(axis=1, mapper=column_name_mapper)

contracts_df['tag'] = contracts_df['tag'].fillna('').astype(str)
contracts_df['tag'] = contracts_df['tag'].str.strip(to_strip="['").str.strip(to_strip="']")

contracts_df['Suppler Name'] = contracts_df['Supplier Name'].fillna('').astype(str)
"""
contracts_df['Zaizi'] = contracts_df['Supplier Name'].str.contains('Zaizi', case=False, na=False)


contracts_df.to_csv("./data/from_jan_govt_contracts.csv")


