import google.generativeai as genai
from google.generativeai.types import Tool 
from google.generativeai.protos import FunctionResponse
import asyncio
import os
import json
from fastmcp import Client 
from fastmcp.client.transports import PythonStdioTransport 
from mcp.types import TextContent
from server.tools.declarations import summarise_csv
from dotenv import load_dotenv
load_dotenv()


MCP_SERVER_SCRIPT_PATH = os.getenv("MCP_SERVER_SCRIPT_PATH")
#Initialize the FastMCP Client
mcp_client = Client(
     transport=PythonStdioTransport(python_cmd=os.sys.executable, script_path=MCP_SERVER_SCRIPT_PATH)
)


summarise_csv_file_tool_declaration = summarise_csv.summarise_csv_file_tool_declaration

gemini_tools = [
    Tool(function_declarations=[summarise_csv_file_tool_declaration])
]

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

# --- Initialize Gemini Model --- 
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    tools=gemini_tools
)


# Asynchronous Function to Call the MCP
async def call_mcp_server_tool_async(tool_name: str, args: dict) -> dict:
    """
    Asynchronously calls a specific tool on your MCP server via STDIO.
    """
    try:
        # This async with block ensures the client is properly connected and manages the server subprocess. 
        async with mcp_client: #Context manager -- important
            result = await mcp_client.call_tool(tool_name, args)
            return result
    except Exception as e:
        return {"error": f"MCP Server Tool Error: {e}"}


# --- Main Asynchronous Chat Loop and Response Handler ---
async def handle_gemini_response_async(chat_session, gemini_response):
    """
    Asynchronously processes Gemini's response, handling text output or required function calls.
    """
    for part in gemini_response.parts:
        if part.text:
            print(f"Gemini: {part.text}")
        elif part.function_call:
            function_call = part.function_call
            print(f"[DEBUG] Gemini wants to call: {function_call.name} with args: {function_call.args}")

            tool_output = None

            if function_call.name == "summarize_csv_file":
                filename = function_call.args.get('filename')
                if not filename:
                    print("[INFO] 'summarize_csv_file' called without a filename. Prompting user for input.")
                    tool_output = {"info": "The user did not provide a filename. You must ask the user for the name of the file to summarize."}
                else:
                    tool_output = await call_mcp_server_tool_async(function_call.name, {'filename': filename})
            else:
                print(f"[ERROR] Gemini called an unrecognized tool: {function_call.name}")
                tool_output = {"error": f"Unknown tool called by Gemini: {function_call.name}"}

            response_data = {}
            if isinstance(tool_output, list) and all(isinstance(item, TextContent) for item in tool_output):
                text_result = "\n".join([content.text for content in tool_output])
                response_data = {"result": text_result}
    
            elif isinstance(tool_output, dict): 
                response_data = tool_output
            else:
                response_data = {"error": "Received an unexpected output format from the tool."}
                print(f"[ERROR] Unexpected tool output format: {tool_output}")

            print(f"[DEBUG] Sending tool output back to Gemini: {response_data}")
            await chat_session.send_message_async(FunctionResponse(
                name=function_call.name,
                response=response_data
            ))

            final_gemini_response = chat_session.last.text
            print(f"Gemini (final response): {final_gemini_response}")