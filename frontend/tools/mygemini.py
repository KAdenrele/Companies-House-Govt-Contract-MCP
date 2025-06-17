import google.generativeai as genai
from google.generativeai.types import Tool 
from google.generativeai.protos import FunctionResponse
import os
from fastmcp import Client 
from fastmcp.client.transports import StreamableHttpTransport
from mcp.types import TextContent
import logging
from tools.declarations import summarise_csv
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
transport = StreamableHttpTransport(url=MCP_SERVER_URL)
mcp_client = Client(transport=transport)


summarise_csv_file_tool_declaration = summarise_csv.summarise_csv_file_tool_declaration

gemini_tools = [
    Tool(function_declarations=[summarise_csv_file_tool_declaration])
]

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    tools=gemini_tools
)


# Asynchronous Function to Call the MCP
async def call_mcp_server_tool_async(tool_name: str, args: dict) -> dict:
    """
    Asynchronously calls a specific tool on the MCP server via HTTP.
    """
    logger.debug(f"Calling MCP server tool '{tool_name}' with args: {args}")
    try:
        # The async with block ensures the client is properly managed.
        async with mcp_client:
            result = await mcp_client.call_tool(tool_name, args)
            return result
    except Exception as e:
        logger.error(f"Error communicating with MCP server tool '{tool_name}'", exc_info=True)
        return {"error": f"MCP Server Tool Error: {e}"}


# --- Main Handler Function ---
async def handle_gemini_response_async(chat_session, gemini_response):
    """
    Asynchronously processes Gemini's response, delegating tool calls to a helper function.
    """
    for part in gemini_response.parts:
        if part.text:
            logger.info(f"Gemini returned direct text: {part.text}")
            return part.text
        
        elif part.function_call:
            function_call = part.function_call
            logger.debug(f"Gemini wants to call: {function_call.name} with args: {function_call.args}")

            tool_output = None

            if function_call.name == "summarise_csv_file":
                filename = function_call.args.get('filename')
                if not filename:
                    logger.info("summarise_csv_file' called without a filename.")
                    tool_output = {"info": "The user did not provide a filename. You must ask the user for the name of the file to summarise."}
                else:

                    tool_output = await call_mcp_server_tool_async(function_call.name, {'filename': filename})
            else:
                logger.error(f"Gemini called an unrecognized tool: {function_call.name}")
                tool_output = {"error": f"Unknown tool called by Gemini: {function_call.name}"}

            response_data = {}
            if isinstance(tool_output, list) and all(isinstance(item, TextContent) for item in tool_output):
                text_result = "\n".join([content.text for content in tool_output])
                response_data = {"result": text_result}
            elif isinstance(tool_output, dict): 
                response_data = tool_output
            else:
                response_data = {"error": "Received an unexpected output format from the tool."}
                logger.warning(f"Unexpected tool output format: {tool_output}")

            logger.debug(f"Sending tool output back to Gemini: {response_data}")
            await chat_session.send_message_async(FunctionResponse(
                name=function_call.name,
                response=response_data
            ))

            final_gemini_response = chat_session.last.text
            logger.info(f"Gemini returned text after tool call: {final_gemini_response}")
            return final_gemini_response