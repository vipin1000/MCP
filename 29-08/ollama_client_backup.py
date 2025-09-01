# import asyncio
# import nest_asyncio

# nest_asyncio.apply()

# from llama_index.llms.ollama import Ollama
# from llama_index.core import Settings
# from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
# from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
# from llama_index.core.workflow import Context


# # Initialize LLM
# # llm = Ollama(model="mistral")
# llm = Ollama(model="mistral")
# Settings.llm = llm

# # System prompt for the agent
# SYSTEM_PROMPT = """\
# You are an AI assistant for Tool Calling.

# Before you help a user, you need to work with tools to interact with Our Database
# """


# # Create agent
# async def get_agent(tools: McpToolSpec):
#     tools = await tools.to_tool_list_async()
#     agent = FunctionAgent(
#         name="Agent",
#         description="An agent that can work with Our Database software.",
#         tools=tools,
#         llm=llm,
#         system_prompt=SYSTEM_PROMPT,
#     )
#     return agent


# # Handle user messages
# async def handle_user_message(
#     message_content: str,
#     agent: FunctionAgent,
#     agent_context: Context,
#     verbose: bool = False,
# ):
#     handler = agent.run(message_content, ctx=agent_context)
#     async for event in handler.stream_events():
#         if verbose and isinstance(event, ToolCall):
#             print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
#         elif verbose and isinstance(event, ToolCallResult):
#             print(f"Tool {event.tool_name} returned {event.tool_output}")

#     response = await handler
#     return str(response)


# # Main entry point
# async def main():
#     mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
#     mcp_tool = McpToolSpec(client=mcp_client)

#     # Initialize agent
#     agent = await get_agent(mcp_tool)
#     agent_context = Context(agent)

#     # REPL loop
#     while True:
#         user_input = input("Enter your message: ")
#         if user_input.strip().lower() == "exit":
#             print("Exiting...")
#             break
#         print("User: ", user_input)
#         response = await handle_user_message(user_input, agent, agent_context, verbose=True)
#         print("Agent: ", response)


# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio
import nest_asyncio

nest_asyncio.apply()

from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
from llama_index.core.workflow import Context


# Initialize LLM - optimized for 3B model
llm = Ollama(
    model="llama3.2:3b", 
    temperature=0.0,  # More deterministic for small models
    top_p=0.9,        # Reduce randomness
    repeat_penalty=1.1
)
Settings.llm = llm

SYSTEM_PROMPT = """\
You are a helpful AI assistant that MUST use tools to complete tasks.

CRITICAL RULES:
1. ALWAYS use tools when asked about data, files, or databases
2. Do NOT make up information - use tools to get real data
3. For database tasks: use database tools (create_table, insert_data, select_data)
4. For file tasks: use file tools (list_files, read_json_file, write_json_file)
5. Break complex tasks into simple steps
6. Use one tool at a time and explain what you're doing

Examples:
- User asks "what files are here?" → Use list_files tool
- User asks "create a table" → Use create_table tool
- User asks "show me data" → Use select_data tool

You have access to many tools. Use them!
"""


async def get_agent(tools: McpToolSpec):
    """Create and configure the function agent with MCP tools"""
    try:
        tools_list = await tools.to_tool_list_async()
        print(f"Loaded {len(tools_list)} tools from MCP server")
        
        agent = FunctionAgent(
            name="MCPAgent",
            description="An agent that can work with databases and files through MCP tools.",
            tools=tools_list,
            llm=llm,
            system_prompt=SYSTEM_PROMPT,
            max_function_calls=5,  # Reduced for 3B model
            verbose=True
        )
        return agent
    except Exception as e:
        print(f"Error creating agent: {e}")
        raise


async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = True,
):
    """Handle user messages with proper error handling and tool call tracking"""
    try:
        handler = agent.run(message_content, ctx=agent_context)
        
        tool_calls_made = []
        async for event in handler.stream_events():
            if isinstance(event, ToolCall):
                tool_calls_made.append(event.tool_name)
                if verbose:
                    print(f"🔧 Calling tool: {event.tool_name}")
                    print(f"   Parameters: {event.tool_kwargs}")
            elif isinstance(event, ToolCallResult):
                if verbose:
                    print(f"✅ Tool {event.tool_name} completed")
                    print(f"   Result: {str(event.tool_output)[:200]}...")  # Truncate long outputs

        response = await handler
        
        if verbose and not tool_calls_made:
            print("⚠️  No tools were called. The agent may not be using tools properly.")
            
        return str(response)
        
    except Exception as e:
        print(f"Error handling message: {e}")
        return f"Sorry, I encountered an error: {str(e)}"


async def test_mcp_connection(mcp_client):
    """Test the MCP server connection"""
    try:
        # Try to create a tool spec to test connection
        mcp_tool = McpToolSpec(client=mcp_client)
        tools = await mcp_tool.to_tool_list_async()
        print(f"✅ MCP server connected successfully! Available tools: {len(tools)}")
        for tool in tools[:5]:  # Show first 5 tools
            print(f"   - {tool.metadata.name}: {tool.metadata.description}")
        if len(tools) > 5:
            print(f"   ... and {len(tools) - 5} more tools")
        return True
    except Exception as e:
        print(f"❌ MCP server connection failed: {e}")
        return False


async def main():
    """Main application loop with better error handling"""
    print("🚀 Starting MCP Agent...")
    
    try:
        # Initialize MCP client
        print("1")
        mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
        
        # Test connection first
        print("2")
        if not await test_mcp_connection(mcp_client):
            print("Cannot proceed without MCP server connection.")
            return
        print("2")    
        mcp_tool = McpToolSpec(client=mcp_client)
        print("3")
        # Initialize agent
        print("🤖 Creating agent...")
        agent = await get_agent(mcp_tool)
        agent_context = Context(agent)
        
        print("✅ Agent ready! Type 'exit' to quit, 'help' for example commands.")
        print("-" * 50)
        
        # REPL loop
        while True:
            try:
                user_input = input("\n👤 Enter your message: ").strip()
                
                if user_input.lower() == "exit":
                    print("👋 Exiting...")
                    break
                elif user_input.lower() == "help":
                    print("""
📋 Example commands you can try:
- "List all files in the current directory"
- "Create a table called 'users' with columns: id (integer), name (text), email (text)"
- "Show me what's in the database"
- "Add a new user with name 'John' and email 'john@example.com'"
- "Read the contents of config.json"
                    """)
                    continue
                elif not user_input:
                    continue
                
                print(f"\n👤 User: {user_input}")
                print("🤖 Agent: Processing...")
                
                response = await handle_user_message(user_input, agent, agent_context, verbose=True)
                print(f"\n🤖 Agent: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("Make sure your MCP server is running on http://127.0.0.1:8000")


if __name__ == "__main__":
    asyncio.run(main())