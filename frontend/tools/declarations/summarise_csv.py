from google.generativeai.types import FunctionDeclaration


summarise_csv_file_tool_declaration = FunctionDeclaration(
    name="summarise_csv_file", 
    description="Summarise a CSV file by describing its content",
    parameters={
        "type": "OBJECT",
        "properties": {
            "filename": {
                "type": "STRING",
                "description": "Name of the CSV file in the /data directory (e.g., 'sample.csv')"
            }
        },
        "required": ["filename"]  #commenting this out so that the filename is not required.
    }
)