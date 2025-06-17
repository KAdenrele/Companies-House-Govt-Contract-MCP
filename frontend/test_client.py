import asyncio
import os
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from dotenv import load_dotenv
load_dotenv()


MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
transport = StreamableHttpTransport(url=MCP_SERVER_URL)
mcp_client = Client(transport=transport)


async def test():
    print(f"Attempting to connect to MCP server at: {MCP_SERVER_URL}")
    async with mcp_client:
        await mcp_client.ping()
        print("ping successful")

        tools = await mcp_client.list_tools()
        print(f"Available tools: {tools}")

if __name__ == "__main__":
    asyncio.run(test())

