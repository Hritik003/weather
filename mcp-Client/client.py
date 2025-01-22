import asyncio
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class MCPClient:
    def __init__(self):
        
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        
    
    ## Server connection
        
    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server
    
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
        
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command, 
            args=[server_script_path],
            env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        response = await self.session.list_tools()
        tools = response.tools
        print("\n voila! connected to the server with the tools:",[tool.name for tool in tools])
        
    
    ## Query processing
    
    async def process_query(self, query:str) -> str:
        messages = [
            {
                "role:":"client",
                "query":query
            }
        ]
        
        response = await self.session.list_tools()
        available_tools = [{
            "name":tool.name,
            "description":tool.description,
            "inputSchema":tool.inputSchema
        }for tool in response.tools]
        
        response = self.anthropic.messages.create(
            model = "claude-3-5-sonnet-20241022",
            max_tokens = 100,
            messages = messages,
            tools = available_tools
        )
        
        tool_results=[]
        final_text=[]
        
        for content in response.content:
            if content.type =='text':
                final_text.append(content.text)
            elif content.type =='tool_use':
                tool_name = content.name
                tool_args = content.input
                
                #tool call
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call":tool_name,"result":result})
                final_text.append(f"[calling tool {tool_name} with args {tool_args}] ")
                
                #continue conv with tool results
                if hasattr(content, 'text') and content.text:
                    messages.append({
                        "role":"assistant",
                        "content":content.text
                    })
                
                messages.append({
                    "role":"user",
                    "content":result.content
                })
                
                # Get next response from claude
                response = self.anthropic.messages.create(
                    model = "claude-3-5-sonnet-20241022",
                    max_tokens = 100,
                    messages = messages
                )
                
                final_text.append(response.content[0].text)
            
        return "\n".join(final_text)
    
    ## Interactive Chat Interface
    
    async def chat(self):
        """Run an interactive chat interface."""
        print("MCP Client Chat Interface")
        print('Type your queries or "exit" to quit.')
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() =='quit':
                    break
                response = await self.process_query(query)
                print("\n"+response)
            
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
        
async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <server_script_path>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat()
    finally:
        await client.cleanup()
        
if __name__ == "__main__":
    asyncio.run(main())
            
            
        
        
        
        
    
        