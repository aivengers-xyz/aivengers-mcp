import asyncio
import aiohttp
import json
import os

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.server.websocket
import mcp.types as types
import mcp.server.stdio

BACKEND_URL = "https://backend.agiverse.io"
API_KEY = os.getenv("AGIVERSE_API_KEY")

server = Server("aivengers-mcp")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="search_tools",
            description="Search for tools. The tools cover a wide range of domains include data source, API, SDK, etc. Try searching whenever you need to use a tool.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for tools, you can describe what you want to do or what tools you want to use"
                    },
                    "limit": {
                        "type": "number",
                        "description": "The maximum number of tools to return, must be between 1 and 100, default is 10, recommend at least 10"
                    }
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="call_tool",
            description="Call a tool returned by search_tools",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "The exact action you want to call in the search_tools result."
                    },
                    "payload": {
                        "type": "string",
                        "description": "Action payload, based on the payload schema in the search_tools result. You can pass either the json object directly or json encoded string of the object.",
                    },
                    "payment": {
                        "type": "number",
                        "description": "Amount to authorize in USD. Positive number means you will be charged no more than this amount, negative number means you are requesting to get paid for at least this amount.",
                    }
                },
                "required": ["action", "payload"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict = {}
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name == "search_tools":
        query = arguments.get("query")
        
        if not query:
            raise ValueError("Missing query")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{BACKEND_URL}/api/v1/actions/search",
                    params=arguments,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    response.raise_for_status()
                    results = await response.json()
                    return [
                        types.TextContent(
                            type="text", 
                            text=json.dumps(results)
                        )
                    ]
            except Exception as e:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error searching actions: {str(e)}"
                    )
                ]
    elif name == "call_tool":
        action = arguments.get("action")
        payload = arguments.get("payload", {})
        payment = arguments.get("payment", 0)

        if not action:
            raise ValueError("Missing action")

        async with aiohttp.ClientSession() as session:
            try:
                data = {
                    "apiKey": API_KEY,
                    "action": action,
                    "payload": payload,
                    "payment": payment,
                }
                
                async with session.post(
                    f"{BACKEND_URL}/api/v1/actions/call",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps(result)
                        )
                    ]
            except Exception as e:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error calling action: {str(e)}"
                    )
                ]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="aivengers-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
