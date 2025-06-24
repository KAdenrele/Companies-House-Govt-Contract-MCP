import google.generativeai as genai
from google.generativeai.types import Tool
from google.generativeai.protos import FunctionResponse
import os
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from mcp.types import TextContent
import logging
from tools.declarations import summarise_csv, company_information
from tools.companies_house import get_competitors
from dotenv import load_dotenv

# This part is fine
load_dotenv()
logger = logging.getLogger(__name__)
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")


def create_gemini_model():
    """
    Configures and creates the Gemini GenerativeModel instance.
    """
    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=gemini_api_key)

        summarise_csv_file_tool_declaration = summarise_csv.summarise_csv_file_tool_declaration
        company_profile_declaration = company_information.get_company_profile_declaration
        gemini_tools = [
            Tool(function_declarations=[summarise_csv_file_tool_declaration, company_profile_declaration])
        ]

        model = genai.GenerativeModel(
            # Using a recommended model name. "gemini-2.0-flash" is not a public model.
            model_name="gemini-1.5-flash",
            tools=gemini_tools
        )
        return model
    

    except Exception as e:
        logger.error(f"Failed to create Gemini model: {e}", exc_info=True)
        return None


async def call_mcp_server_tool_async(tool_name: str, args: dict) -> dict:
    """
    Asynchronously calls a specific tool on the MCP server via HTTP.
    """
    logger.debug(f"Calling MCP server tool '{tool_name}' with args: {args}")
    try:
        transport = StreamableHttpTransport(url=MCP_SERVER_URL)
        client = Client(transport=transport)
        async with client:
            result = await client.call_tool(tool_name, args)
            return result
    except Exception as e:
        logger.error(f"Error communicating with MCP server tool '{tool_name}'", exc_info=True)
        return {"error": f"MCP Server Tool Error: {e}"}



# The corrected function

async def handle_gemini_response_async(chat_session, initial_gemini_response):
    """
    Asynchronously processes Gemini's response, including handling tool calls
    in a loop until a final text response is available.
    """
    response = initial_gemini_response
    
    while True:
        part = response.parts[0]

        if part.text:
            logger.info(f"Gemini returned final text: {part.text}")
            return part.text

        if not part.function_call:
            logger.warning("Gemini response had no text and no function call. Exiting.")
            return "The model did not provide a text response."

        function_call = part.function_call
        tool_name = function_call.name
        args = {key: value for key, value in function_call.args.items()}
        logger.debug(f"Gemini wants to call: {tool_name} with args: {args}")

        if tool_name == "summarise_csv_file":
            filename = args.get('filename')
            if not filename:
                tool_output = {"info": "The user did not provide a filename. You must ask the user for the name of the file to summarise."}
            else:
                tool_output = await call_mcp_server_tool_async(tool_name, {'filename': filename})
        elif tool_name == "get_company_profile":
            companyNumber = args.get('CompanyNumber')
            if not companyNumber:
                # Fetch a list of companies the user can choose from
                known_companies = get_competitors()
                company_list_str = "\n - ".join([f"{company['name']} (Number: {company['number']})" for company in known_companies])
                tool_output = {
                    "info": f"A Company Number is required. Please ask the user to specify one of the following known companies:\n - {company_list_str}"
                }
            else:
                tool_output = await call_mcp_server_tool_async(tool_name, {'CompanyNumber': companyNumber})

        else:
            logger.info(f"Calling generic tool: {tool_name}")
            tool_output = await call_mcp_server_tool_async(tool_name, args)

        logger.debug(f"Received tool output: {tool_output}")

        # Ensure the data sent back to the model is always a dictionary.
        response_data = {}
        if isinstance(tool_output, list):
            # If the output is a list, convert it to a dictionary.
            text_result = "\n".join([str(item) for item in tool_output])
            response_data = {"result": text_result}
            logger.debug(f"Converted list output to dict: {response_data}")
        elif isinstance(tool_output, dict):
            response_data = tool_output
        else:
            response_data = {"error": "Received an unexpected output format from the tool."}
            logger.warning(f"Unexpected tool output format: {type(tool_output)}")

        response = await chat_session.send_message_async(
            FunctionResponse(name=tool_name, response=response_data)
        )