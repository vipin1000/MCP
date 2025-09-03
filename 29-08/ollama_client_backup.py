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




# import asyncio
# from mcp.client.session import ClientSession
# from mcp.types import CallToolRequest
# from mcp.client.stdio import connect_stdio  # ✅ correct function
# import ollama
# import textwrap


# MODEL = "llama3.2:3b"
# CHUNK_SIZE = 20000


# def chunk_text(text: str, size: int = CHUNK_SIZE):
#     return textwrap.wrap(text, size)


# def summarize_with_ollama(prompt: str) -> str:
#     response = ollama.chat(
#         model=MODEL,
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return response["message"]["content"].strip()


# def summarize_pdf_text(text: str) -> str:
#     chunks = chunk_text(text, CHUNK_SIZE)
#     partial_summaries = []

#     print(f"📄 Splitting PDF into {len(chunks)} chunks...")

#     for i, chunk in enumerate(chunks, 1):
#         print(f"📝 Summarizing chunk {i}/{len(chunks)}...")
#         prompt = f"Summarize the following PDF content into bullet points:\n\n{chunk}"
#         summary = summarize_with_ollama(prompt)
#         partial_summaries.append(summary)

#     print("🔄 Generating final consolidated summary...")
#     merged_prompt = "Combine these chunk summaries into one coherent executive summary:\n\n" + "\n\n".join(partial_summaries)
#     return summarize_with_ollama(merged_prompt)


# async def main():
#     print("🚀 Starting PDF Summarizer Agent with ollama.chat...")

#     async with connect_stdio("server.py") as (read_stream, write_stream):
#         client = ClientSession(read_stream, write_stream)
#         await client.initialize()

#         print("✅ Connected to MCP server!")

#         while True:
#             user_input = input("\n👤 Enter command (e.g. summarize pdf file.pdf or exit): ")
#             if user_input.strip().lower() == "exit":
#                 break

#             if user_input.startswith("summarize pdf"):
#                 _, _, file_path = user_input.partition("pdf")
#                 file_path = file_path.strip()

#                 tool_call = CallToolRequest(name="read_pdf", arguments={"file_path": file_path})
#                 result = await client.call_tool(tool_call)

#                 if result.content and hasattr(result.content[0], "text"):
#                     pdf_text = result.content[0].text
#                     print("📄 Extracted text, sending to Ollama...")

#                     summary = summarize_pdf_text(pdf_text)
#                     print("\n📑 Final Summary:\n", summary)
#                 else:
#                     print("❌ Could not extract text")


# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio
# import nest_asyncio
# import httpx

# nest_asyncio.apply()

# from llama_index.llms.ollama import Ollama
# from llama_index.core import Settings
# from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
# from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
# from llama_index.core.workflow import Context

# # ==========================================================
# # CONFIG
# # ==========================================================
# # 🔗 Replace with your ngrok public FastAPI endpoint
# FASTAPI_URL = "https://37b11cbf9e1c.ngrok-free.app/generate"

# # Initialize LLM
# llm = Ollama(
#     model="mistral",
#     temperature=0.0,  # Deterministic
#     top_p=0.9,
#     repeat_penalty=1.1,
# )
# Settings.llm = llm

# SYSTEM_PROMPT = """\
# You are a helpful AI assistant that MUST use tools to complete tasks.

# RULES:
# 1. ALWAYS use tools when asked about data, files, or databases
# 2. Do NOT make up information - use tools to get real data
# 3. For database tasks: use database tools (create_table, insert_data, select_data)
# 4. For file tasks: use file tools (list_files, read_json_file, write_json_file)
# 5. Break complex tasks into simple steps
# 6. Use one tool at a time and explain what you're doing
# """


# # ==========================================================
# # MCP Agent Setup
# # ==========================================================
# async def get_agent(tools: McpToolSpec):
#     """Create and configure the function agent with MCP tools"""
#     tools_list = await tools.to_tool_list_async()
#     print(f"✅ Loaded {len(tools_list)} tools from MCP server")

#     agent = FunctionAgent(
#         name="MCPAgent",
#         description="An agent that can work with databases and files through MCP tools.",
#         tools=tools_list,
#         llm=llm,
#         system_prompt=SYSTEM_PROMPT,
#         max_function_calls=5,
#         verbose=True,
#     )
#     return agent


# async def handle_user_message(message_content: str, agent: FunctionAgent, agent_context: Context):
#     """Handle user messages with tool usage"""
#     handler = agent.run(message_content, ctx=agent_context)

#     tool_output_accum = []  # collect tool outputs

#     async for event in handler.stream_events():
#         if isinstance(event, ToolCall):
#             print(f"🔧 Calling tool: {event.tool_name}")
#             print(f"   Parameters: {event.tool_kwargs}")
#         elif isinstance(event, ToolCallResult):
#             print(f"✅ Tool {event.tool_name} completed")
#             print(f"   Result: {str(event.tool_output)[:200]}...")
#             tool_output_accum.append(str(event.tool_output))

#     response = await handler
#     return "\n".join(tool_output_accum), str(response)


# # ==========================================================
# # FastAPI Communication
# # ==========================================================
# async def send_to_fastapi(data: str, query: str):
#     """Send payload to FastAPI server (Colab via ngrok)"""
#     payload = {"data": data, "query": query}
#     async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
#         resp = await client.post(FASTAPI_URL, json=payload)
#         resp.raise_for_status()
#         return resp.json()


# # ==========================================================
# # Main
# # ==========================================================
# async def main():
#     print("🚀 Starting MCP Agent...")

#     mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
#     mcp_tool = McpToolSpec(client=mcp_client)

#     # Initialize agent
#     agent = await get_agent(mcp_tool)
#     agent_context = Context(agent)

#     print("✅ Agent ready! Type 'exit' to quit.")
#     print("-" * 50)

#     while True:
#         user_input = input("\n👤 Enter your message: ").strip()
#         if user_input.lower() == "exit":
#             print("👋 Exiting...")
#             break

#         print(f"\n👤 User: {user_input}")
#         print("🤖 Agent: Processing...")

#         tool_result, agent_response = await handle_user_message(user_input, agent, agent_context)

#         # Send tool outputs + user query to FastAPI
#         try:
#             llm_response = await send_to_fastapi(tool_result, user_input)
#             print(f"\n🤖 Final Answer (from FastAPI LLM): {llm_response}")
#         except Exception as e:
#             print(f"❌ Error sending to FastAPI: {e}")


# if __name__ == "__main__":
#     asyncio.run(main())









