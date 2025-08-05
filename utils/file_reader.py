import os
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
from pathlib import Path
from datetime import date
from typing import Optional
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s  - %(message)s')

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def read_csv_summary(filename: str) -> str:
    """
    Read a CSV file and return a simple summary.
    Args:
        filename: Name of the CSV file (e.g. 'sample.csv')
    Returns:
        A string describing the file's contents.
    """
    file_path = DATA_DIR / filename
    df = pd.read_csv(file_path)
    #return f"CSV file '{filename}' has {len(df)} rows and {len(df.columns)} columns. More information {df.describe()} and as a whole is {df}"
    return f"CSV file info is '{df.info()}' and the description is '{df.describe()}'"

def read_parquet_summary(filename: str) -> str:
    """
    Read a Parquet file and return a simple summary.
    Args:
        filename: Name of the Parquet file (e.g. 'sample.parquet')
    Returns:
        A string describing the file's contents.
    """
    file_path = DATA_DIR / filename
    df = pd.read_parquet(file_path)
    return f"Parquet file '{filename}' has {len(df)} rows and {len(df.columns)} columns."

def read_pdf_to_text(DATA_DIR:Path, file)->dict:
    custom_config = r'--psm 6'
    document ={}
    file = str(file)
    document[file]={}

    try:
        with open(os.path.join(DATA_DIR, file), 'rb') as f:
            pdf_file = convert_from_bytes(f.read())
    except Exception as e:
        print(f"Failed to read or convert {file} due to: {e}")
        return document
    

    for (i,page) in enumerate(pdf_file) :
        try:
            page_data= pytesseract.image_to_string(image=page, 
                                                    config=custom_config, 
                                                    output_type= pytesseract.Output.DICT)
            document[file][i] = page_data['text']
        except Exception as e:
            print(f"Failed page {i+1} in {file} due to: {e}")
    return document


class ContractAnalyser:
    """
    A class to load and analyze government contract data from a CSV file.
    """
    def __init__(self, data_dir: Path = DATA_DIR, file_name: str = "from_jan_govt_contracts.csv", year: int = date.today().year):
        """
        Initializes the analyzer, loads and processes the contract data.

        Args:
            data_dir (Path): The directory where the data file is located.
            file_name (str): The name of the CSV file.
            year (int): The year to filter the analysis for. Defaults to the current year.
        """
        self.file_path = data_dir / file_name
        self.year = year        
        self.contracts_df: Optional[pd.DataFrame] = None

        
        self._load_and_prepare_data()

    def _load_and_prepare_data(self):
        """Loads and performs initial cleaning and transformation of the data."""
        try:

            df = pd.read_csv(self.file_path,low_memory=False, usecols=[
                                                                        'Award ID','Award Status','Award Date',  "Award Year", "Award Month", "Award Day",
                                                                        'Data Award Published', 'Award Value', 'Award Value Currency',	
                                                                        'Contracted Period Start Date',	'Contracted Period End Date',	
                                                                        'Award Description','OCID', 'Contract ID', 'Tender ID',
                                                                        'Tender Title','Party ID','Party Name', 'Buyer ID', 'Buyer Name', 'Supplier ID', 'Supplier Name','Zaizi'
                                                                        ])
            #This year only, note you did this. 
            self.contracts_df = df[df['Award Year'] == self.year].copy()

            logger.info("Dataframe has been generated.")
        
        except FileNotFoundError:
            logger.error(f"Error: The file was not found at {self.file_path}")

        except Exception as e:
            logger.error(f"An error occurred during data loading: {e}")