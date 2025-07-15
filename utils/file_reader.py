import os
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
from pathlib import Path

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
    return f"CSV file info is '{df.info()}' and as a whole is '{df}'"

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

