from google.adk.agents import Agent, SequentialAgent, LlmAgent
from google.adk.tools import FunctionTool, ToolContext, AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams,StreamableHTTPConnectionParams
from mcp import StdioServerParameters
from google.adk.models.google_llm import Gemini

from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import InMemoryRunner,Runner
from google.adk.apps.app import App, ResumabilityConfig
import os
import random
from dotenv import load_dotenv
import asyncio

import time
import vertexai
from vertexai import agent_engines


load_dotenv(r'monday_bi_agent/.env') #give path for .env file
MONDAY_API_KEY = os.getenv('your_monday_API_key')

if not MONDAY_API_KEY:
    raise ValueError("MONDAY_API_KEY not found in .env file")
else:
    print("MONDAY_API_KEY found in .env file")

vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
)

retry_config = types.HttpRetryOptions(
    attempts = 5,
    exp_base = 7,
    initial_delay = 1,
    http_status_codes = [429, 500, 503, 504]
)

monday_mcp_server = McpToolset(
        connection_params = StreamableHTTPConnectionParams(
            url = "https://mcp.monday.com/mcp",
            headers = {
                "Authorization": MONDAY_API_KEY,
            }
        )
    )


query_agent = Agent(
    model = Gemini(model = 'gemini-2.5-flash', retry_options = retry_config),
    name = 'query_agent',
    description = 'an agent which get basic required details from user for getting work done.',
    instruction = '''when user ask question related to monday workspace or boards then ask for required details
    1.always clarify what user is asking if needed ask some more details
    2. store the workspace id and board id in the output key 'workspace_id' and 'board_id'.
    3. use monday_mcp_server tool to get the available workspaces and boards.
    example:
    user : hi can you get me details of sakura.
    Available Workspaces and Boards:
    1. Workspace: 'Executive Operations'
       - Board: 'Work Orders Q1' (ID: 112233)
       - Board: 'Enterprise Deals' (ID: 445566)
    user: go with workspace id 112233
    2. Workspace: 'Archived'
       - Board: 'Old Deals' (ID: 778899)
    user : go with board id 778899
    note: until user selects any workspace or board don't continue to next step and only use 
    user specified workspace id and board id.and keep the reponse short and simple no unnecessary
    details or response.
    ''',
    tools = [monday_mcp_server],
    output_key = 'query_agent',
)

extract_agent = Agent(
    model = Gemini(model = 'gemini-2.5-flash-lite', retry_options = retry_config),
    name = 'extract_agent',
    description = '''a helpful conversational assistant which act as a founder personal agent to answer
    business related questions from monday.com using the given tools of provided main workspace.''',
    instruction = '''always answer in simple language and easy to understand.
    1.try to use ReAct framework to answer question.
    2.always reason with yourself before taking action then act and observe what it does.
    3.self reflect and correct your path and answer to suit the user query and don't overdo the reasoning and reflection.
    4.use query_agent output to get the workspace id and board id.
    5.based on the selected workspace id and board id then use available tools and their output keys to answer the query.
    6. if user ask out of scope question other than monday workspace related then answer politely to ask for question related
    to monday workspace.
    . Thought: Reason about what the founder is asking. What data sources do you need?
    . Action: Call the appropriate fetch tool(s) to get live data.
    . Observe: Look at the raw data returned.
    . Thought: Notice that the data is messy. Decide how to clean it.
    . Action: Call the clean_and_normalize_data tool.
    . Observe: Look at the cleaned data.
    . Thought: Formulate business intelligence insights (e.g., revenue, pipeline health, sector performance).
    . Action: clean the data of any missing values or inconsistent data dont add any data but show user the data as is is but say not specified. show whatever data avaialbel for inconsistent data.
    . Final Answer: Provide a concise, founder-level summary with your insights and explicitly state any caveats about missing or inconsistent data.

    ''',
    tools = [monday_mcp_server],
    output_key = 'extract_agent',
)

root_agent = LlmAgent(
    model = Gemini(model = 'gemini-2.5-flash', retry_options = retry_config),
    name = 'root_agent',
    description = 'personal assistant which takes user query and perform task using the monday tools.',
    instruction = '''always answer in simple and short form dont use unnecessary details and long explanation
    1.use query_agent and extract_agent to get the workspace id and board id.
    2.based on the selected workspace id and board id then use available tools and their output keys to answer the query.
    3. if user ask out of scope question other than monday workspace related then answer politely to ask for question related
    to monday workspace.
    ''',
    tools = [AgentTool(agent = query_agent), AgentTool(agent = extract_agent)],
    output_key = 'root_agent',

)

monday_app = App(
    name = 'monday_app',
    root_agent = root_agent,
    resumability_config = ResumabilityConfig(is_resumable = True)
)

session_service = InMemorySessionService()
runner = Runner(
    app = monday_app,
    session_service = session_service,
)

if __name__ == "__main__":
    response = asyncio.run(runner.run_debug("sakura"))
    print(response)