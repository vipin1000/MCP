# import asyncio
# import nest_asyncio

# nest_asyncio.apply()

# from llama_index.llms.ollama import Ollama
# from llama_index.core import Settings
# from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
# from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
# from llama_index.core.workflow import Context


# # -----------------------------------------------------
# # Configure LLM (optimized for smaller models like 3B)
# # -----------------------------------------------------
# llm = Ollama(
#     model="llama3.2:3b", 
#     temperature=0.0,
#     top_p=0.9,
#     repeat_penalty=1.1
# )
# Settings.llm = llm


# SYSTEM_PROMPT = """\
# You are a helpful AI assistant that MUST use tools to complete tasks.

# CRITICAL RULES:
# 1. Always use the PDF tool when the user asks about reading or analyzing PDFs
# 2. Do NOT make up PDF contents — use the read_pdf tool
# 3. Keep responses concise but accurate
# 4. If asked for a summary, call read_pdf first, then summarize the results
# """


# # -----------------------------------------------------
# # Agent Setup
# # -----------------------------------------------------
# async def get_agent(tools: McpToolSpec):
#     tools_list = await tools.to_tool_list_async()
#     print(f"✅ Loaded {len(tools_list)} tools from MCP server")
    
#     for tool in tools_list:
#         print(f"   - {tool.metadata.name}: {tool.metadata.description}")
    
#     return FunctionAgent(
#         name="PDF_Agent",
#         description="An agent that can read and summarize PDF files.",
#         tools=tools_list,
#         llm=llm,
#         system_prompt=SYSTEM_PROMPT,
#         max_function_calls=3,
#         verbose=True
#     )


# # -----------------------------------------------------
# # Handle user input
# # -----------------------------------------------------
# async def handle_user_message(message_content: str, agent: FunctionAgent, agent_context: Context):
#     handler = agent.run(message_content, ctx=agent_context)
    
#     async for event in handler.stream_events():
#         if isinstance(event, ToolCall):
#             print(f"🔧 Calling tool: {event.tool_name}")
#             print(f"   Parameters: {event.tool_kwargs}")
#         elif isinstance(event, ToolCallResult):
#             print(f"✅ Tool {event.tool_name} completed")
#             preview = str(event.tool_output)
#             print(f"   Result preview: {preview[:200]}...")
    
#     response = await handler
#     return str(response)


# # -----------------------------------------------------
# # Main Loop
# # -----------------------------------------------------
# async def main():
#     print("🚀 Starting PDF Agent with MCP tools...")
    
#     mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
#     mcp_tool = McpToolSpec(client=mcp_client)

#     # Create agent
#     agent = await get_agent(mcp_tool)
#     agent_context = Context(agent)

#     print("\n✅ Agent ready! Type 'exit' to quit")
#     print("💡 Example: 'Read sample.pdf' or 'Summarize report.pdf'")
#     print("-" * 50)

#     while True:
#         user_input = input("\n👤 Enter your message: ").strip()
#         if user_input.lower() == "exit":
#             print("👋 Exiting...")
#             break
#         if not user_input:
#             continue

#         print(f"\n👤 User: {user_input}")
#         print("🤖 Agent: Processing...")

#         response = await handle_user_message(user_input, agent, agent_context)
#         print(f"\n🤖 Agent: {response}")


# if __name__ == "__main__":
#     asyncio.run(main())






import asyncio
import nest_asyncio
import logging
import traceback

nest_asyncio.apply()

from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
from llama_index.core.workflow import Context

# -----------------------------------------------------
# Configure Logging
# -----------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,  # change to INFO in production
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("PDF_Agent")

DEBUG_MODE = True  # set False to disable pdb breakpoints


# -----------------------------------------------------
# Configure LLM (optimized for smaller models like 3B)
# -----------------------------------------------------
llm = Ollama(
    model="llama3.2:3b",
    temperature=0.0,
    top_p=0.9,
    repeat_penalty=1.1
)
Settings.llm = llm


SYSTEM_PROMPT = """\
You are a helpful AI assistant that MUST use tools to complete tasks.

CRITICAL RULES:
1. Always use the PDF tool when the user asks about reading or analyzing PDFs
2. Do NOT make up PDF contents — use the read_pdf tool
3. Keep responses concise but accurate
4. If asked for a summary, call read_pdf first, then summarize the results
"""


# -----------------------------------------------------
# Agent Setup
# -----------------------------------------------------
async def get_agent(tools: McpToolSpec):
    try:
        tools_list = await tools.to_tool_list_async()
        logger.info("✅ Loaded %d tools from MCP server", len(tools_list))
        for tool in tools_list:
            logger.debug("   - %s: %s", tool.metadata.name, tool.metadata.description)

        return FunctionAgent(
            name="PDF_Agent",
            description="An agent that can read and summarize PDF files.",
            tools=tools_list,
            llm=llm,
            system_prompt=SYSTEM_PROMPT,
            max_function_calls=3,
            verbose=True
        )
    except Exception as e:
        logger.error("❌ Failed to load tools: %s", str(e))
        traceback.print_exc()
        raise


# -----------------------------------------------------
# Handle user input with logging + error capture
# -----------------------------------------------------
async def handle_user_message(message_content: str, agent: FunctionAgent, agent_context: Context):
    try:
        handler = agent.run(message_content, ctx=agent_context)

        async for event in handler.stream_events():
            if isinstance(event, ToolCall):
                logger.info("🔧 Calling tool: %s", event.tool_name)
                logger.debug("   Parameters: %s", event.tool_kwargs)
            elif isinstance(event, ToolCallResult):
                logger.info("✅ Tool %s completed", event.tool_name)
                preview = str(event.tool_output)
                logger.debug("   Result preview: %s...", preview[:200])

        response = await handler
        return str(response)

    except Exception as e:
        logger.error("❌ Error while handling message '%s': %s", message_content, str(e))
        traceback.print_exc()

        if DEBUG_MODE:
            import pdb; pdb.set_trace()

        return f"⚠️ An error occurred while processing your request: {str(e)}"


# -----------------------------------------------------
# Main Loop
# -----------------------------------------------------
async def main():
    logger.info("🚀 Starting PDF Agent with MCP tools...")

    try:
        mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
        mcp_tool = McpToolSpec(client=mcp_client)

        # Create agent
        agent = await get_agent(mcp_tool)
        agent_context = Context(agent)

        print("\n✅ Agent ready! Type 'exit' to quit")
        print("💡 Example: 'Read sample.pdf' or 'Summarize report.pdf'")
        print("-" * 50)

        while True:
            user_input = input("\n👤 Enter your message: ").strip()
            if user_input.lower() == "exit":
                logger.info("👋 Exiting...")
                break
            if not user_input:
                continue

            logger.info("👤 User: %s", user_input)
            logger.info("🤖 Agent: Processing...")

            response = await handle_user_message(user_input, agent, agent_context)
            print(f"\n🤖 Agent: {response}")

    except Exception as e:
        logger.critical("💥 Fatal error in main loop: %s", str(e))
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
