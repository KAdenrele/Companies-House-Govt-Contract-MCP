import requests
import time
from datetime import date, timedelta, datetime
from typing import Optional, List, Dict, Any
import pandas as pd


BASE_URL = "https://www.contractsfinder.service.gov.uk"

def get_all_contracts(publishedFrom: Optional[str] = None,  publishedTo: Optional[str] = None, stage: str = "awarded", size: int = 100) -> List[Dict[str, Any]]:
    
    search_url = f"{BASE_URL}/Published/Notices/OCDS/Search"
    all_results = []
    next_cursor = None
    
    params = {"stage": stage, "size": size}
    if publishedFrom: params["publishedFrom"] = publishedFrom
    if publishedTo: params["publishedTo"] = publishedTo

    while True:
        if next_cursor:
            params['cursor'] = next_cursor
        
        try:
            response = requests.get(search_url, params=params)
            data = response.json()
            
            if not isinstance(data, dict) or not data:
                break 
            
            all_results.extend(data.get("releases",[]))

            next_cursor = response.headers.get("nextCursor") # Or another header name
            
            if not next_cursor:
                break
            
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            break
            
    return all_results

def fetch_contracts_by_interval(start_date_str: str = "2025-01-01", day_interval: int = 2) -> List[Dict[str, Any]]:
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
contracts_df['tender_id'] = contracts_df['tender'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
contracts_df['tender_title'] = contracts_df['tender'].apply(lambda x: x.get('title') if isinstance(x, dict) else None)
contracts_df['party_id'] = contracts_df['parties'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
contracts_df['party_name'] = contracts_df['parties'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
contracts_df['buyer_id'] = contracts_df['buyer'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
contracts_df['buyer_name'] = contracts_df['buyer'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)

awards_df = pd.json_normalize(contracts_df['awards'])
awards_df = awards_df.explode('suppliers').reset_index(drop=True)
awards_df = awards_df.explode('documents').reset_index(drop=True)
awards_df.columns = ['awards_' + col for col in awards_df.columns]

contracts_df = pd.concat([awards_df, contracts_df], axis = 1)
contracts_df['awards_supplier_id'] = contracts_df['awards_suppliers'].apply(lambda x : x.get('id') if isinstance(x, dict) else None )
contracts_df['awards_supplier_name'] = contracts_df['awards_suppliers'].apply(lambda x : x.get('name') if isinstance(x, dict) else None )
contracts_df['awards_document_id'] = contracts_df['awards_documents'].apply(lambda x : x.get('id') if isinstance(x, dict) else None )
contracts_df = contracts_df.drop(columns=["awards", "tender", "parties", "buyer", "awards_suppliers", "awards_documents"])

contracts_df["awards_value.amount"] = pd.to_numeric(contracts_df["awards_value.amount"], errors="raise")
contracts_df["awards_date"] = pd.to_datetime(contracts_df["awards_date"], errors="raise", utc=True)
contracts_df['awards_year'] = contracts_df["awards_date"].dt.year
contracts_df['awards_month'] = contracts_df["awards_date"].dt.month
contracts_df['awards_day'] = contracts_df["awards_date"].dt.day
contracts_df["awards_contractPeriod.startDate"] = pd.to_datetime(contracts_df["awards_contractPeriod.startDate"], errors="raise", utc=True)
contracts_df["awards_contractPeriod.endDate"] = pd.to_datetime(contracts_df["awards_contractPeriod.endDate"], errors="raise", utc=True)

contracts_df["awards_date" ] = contracts_df["awards_date"].dt.strftime('%d-%m-%Y')
contracts_df[ "awards_contractPeriod.startDate"] = contracts_df["awards_contractPeriod.startDate"].dt.strftime('%d-%m-%Y')
contracts_df["awards_contractPeriod.endDate" ] = contracts_df["awards_contractPeriod.endDate" ].dt.strftime('%d-%m-%Y')

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

contracts_df['tag'] = contracts_df['tag'].str.strip(to_strip="['").str.strip(to_strip="']")
contracts_df = contracts_df[contracts_df['tag'] =='award']
contracts_df['Zaizi'] = contracts_df['Supplier Name'].str.contains('Zaizi', case=False, na=False)
contracts_df.to_csv("./data/from_jan_govt_contracts.csv")
