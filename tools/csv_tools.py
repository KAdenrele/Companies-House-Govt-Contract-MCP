from utils.mcp_instance import mcp
from utils.file_reader import read_csv_summary, ContractAnalyser
import pandas as pd

@mcp.tool(name="summarise_csv_file")
def summarise_csv_file(filename: str) -> str:
    """
    Summarise a CSV file by reporting its number of rows and columns.
    Args:
        filename: Name of the CSV file in the /data directory (e.g., 'sample.csv')
    Returns:
        A string describing the file's dimensions.
    """

    if filename is None:
        return {
            "status": "user_guidance", 
            "message": "The file name is unknown. Suggest the user uses'sample.csv' as an example."
            }
    
    return read_csv_summary(filename)

@mcp.tool(name="Read_Govt_Awards_CSV")
def Read_Govt_Awards_CSV():
    """
   
    Loads and returns government contract awards as a list of records.
        
    """

    awards = ContractAnalyser()
    
    return awards.contracts_df.to_dict(orient="records")

