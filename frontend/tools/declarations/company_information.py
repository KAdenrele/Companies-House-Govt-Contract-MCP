from google.generativeai.types import FunctionDeclaration


get_company_profile_declaration = FunctionDeclaration(
    name="get_company_profile", 
    #the second line here might be crucial for the tool to be called without the companyNumber which then triggers the condition for providing the list.
    description="Provide a company profile from companies house." #If the company number is unknown, call the tool without it to get a list of suggestions.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "companyNumber": {
                "type": "STRING",
                "description": "Company number of a company which exists in Companies house"
            }
        },
        #"required": ["companyNumber"]  
    }
)