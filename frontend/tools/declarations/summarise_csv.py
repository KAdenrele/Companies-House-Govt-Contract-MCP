from google.generativeai.types import FunctionDeclaration


summarise_csv_file_tool_declaration = FunctionDeclaration(
    name="summarize_csv_file", 
    #description="Summarize a CSV file by reporting its number of rows and columns. Use this when the user asks for a summary or details about a specific CSV file.",
    description="Summarize a CSV file by describing its content",
    parameters={
        "type": "OBJECT",
        "properties": {
            "filename": {
                "type": "STRING",
                "description": "Name of the CSV file in the /data directory (e.g., 'sample.csv')"
            }
        },
        #"required": ["filename"]  #commenting this out so that the filename is not required.
    }
)