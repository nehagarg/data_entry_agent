# from google.adk.agents.llm_agent import Agent

# root_agent = Agent(
#     model='gemini-2.5-flash',
#     name='root_agent',
#     description='A helpful assistant for user questions.',
#     instruction='Answer user questions to the best of your knowledge',
# )



from google.adk.agents import LoopAgent, LlmAgent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StdioServerParameters, SseConnectionParams, StreamableHTTPConnectionParams
from google.genai import types
from google.adk.models.google_llm import Gemini
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from .sub_agents import logging, retry_config, browser_interaction_agent, browser_interaction_agent_in_seq, pdf_image_parser_agent, STATE_CURRENT_DOC, COMPLETION_PHRASE, STATE_CRITICISM, GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL



from typing import Optional, Dict
from playwright.async_api import async_playwright, Error as PlaywrightError
from mcp_use import MCPClient
import os




# logger = logging.getLogger("google_adk." + __name__)



# Clean up any previous logs
for log_file in ["logger.log", "web.log", "tunnel.log"]:
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"🧹 Cleaned up {log_file}")

# Configure logging with DEBUG log level.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(filename)s:%(lineno)s %(levelname)s:%(message)s",
)

#Commenting out LoopAgent based refinement for as it is working well without it
# from google.adk.tools.tool_context import ToolContext
# # --- Tool Definition ---
# def exit_loop(tool_context: ToolContext):
#   """Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end."""
#   print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
#   tool_context.actions.escalate = True
#   # Return empty dict as tools should typically return JSON-serializable output
#   return {}



# # STEP 2a: Critic Agent (Inside the Refinement Loop)
# critic_agent_in_loop = LlmAgent(
#     name="CriticAgent",
#     model=GEMINI_FLASH_MODEL,
#     include_contents='none',
#     # MODIFIED Instruction: More nuanced completion criteria, look for clear improvement paths.
#     instruction=f"""You are a Constructive Critic AI reviewing a response from the form filling agent. You need to see if the response is correct.

#     **Doc to Review:**
#     ```
#     {{current_response}}
#     ```

#     **Task:**
#     Review the docum.

#     IF you identify 1-2 *clear and actionable* ways the response could be corrected to better finish the form e.g. missing browser_snapshot or fill form in response, retry in case of errors, missing fields in fill form request:
#     Provide these specific suggestions concisely. Output *only* the critique text.

#     ELSE IF the response seems correct and has no glaring errors or obvious omissions:
#     Respond *exactly* with the phrase "{COMPLETION_PHRASE}" and nothing else. It doesn't need to be perfect, just functionally complete for this stage. Avoid suggesting purely subjective stylistic preferences if the core is sound.

#     Do not add explanations. Output only the critique OR the exact completion phrase.
# """,
#     description="Reviews the current response, providing critique if clear improvements are needed, otherwise signals completion.",
#     output_key=STATE_CRITICISM
# )

# # STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
# refiner_agent_in_loop = LlmAgent(
#     name="RefinerAgent",
#     model=GEMINI_FLASH_MODEL,
#     # Relies solely on state via placeholders
#     include_contents='none',
#     instruction=f"""You are a refiner agent refining an llm response OR exiting the process.
#     **Current Response:**
#     ```
#     {{current_response}}
#     ```
#     **Critique/Suggestions:**
#     {{correction}}

#     **Task:**
#     Analyze the 'Corrections'.
#     IF the correction is *exactly* "{COMPLETION_PHRASE}":
#     You MUST call the 'exit_loop' function. Do not output any text.
#     ELSE (the critique contains actionable feedback):
#     Carefully apply the suggestions to improve the 'Current Response'. Output *only* the refined response.

#     Do not add explanations. Either output the refined response OR call the exit_loop function.
# """,
#     description="Refines the response based on critique, or calls exit_loop if critique indicates completion.",
#     tools=[exit_loop], # Provide the exit_loop tool
#     output_key=STATE_CURRENT_DOC # Overwrites state['current_document'] with the refined version
# )



# # STEP 2: Refinement Loop Agent
# refinement_loop = LoopAgent(
#     name="RefinementLoop",
#     # Agent order is crucial: Critique first, then Refine/Exit
#     sub_agents=[
#         critic_agent_in_loop,
#         refiner_agent_in_loop,
#     ],
#     max_iterations=5 # Limit loops
# )



# # STEP 3: Overall Sequential Pipeline
# # For ADK tools compatibility, the root agent must be named `root_agent`
# root_loop_agent = SequentialAgent(
#     name="IterativeFormFillingPipeline",
#     sub_agents=[
#         browser_interaction_agent, # Run first to create initial doc
#         refinement_loop       # Then run the critique/refine loop
#     ],
#     description="Gives an initial respose and then iteratively refines it with critique using an exit tool."
# )


#Commenting out sequential agent as it is working well without it
# my_sequential_agent = SequentialAgent(
#     name="data_entry_sequential_agent",
#     sub_agents=[pdf_image_parser_agent, browser_interaction_agent_in_seq],
#     description="Fills the form by first parsing the document through pdf_image_parser_agent and then interacting with the browser through browser_interaction_agent.",

# )
#root_agent = my_sequential_agent
#root_agent = browser_interaction_agent
#root_agent = root_loop_agent








from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini

# Define the AI model to be used for summarization:
summarization_llm = Gemini(model=GEMINI_FLASH_MODEL)

# Create the summarizer with the custom model:
my_summarizer = LlmEventSummarizer(llm=summarization_llm)

# Configure the App with the custom summarizer and compaction settings:
app = App(
    name='data_entry_agent',
    root_agent=browser_interaction_agent,
    events_compaction_config=EventsCompactionConfig(
        summarizer=my_summarizer,
        compaction_interval=3,
        overlap_size=1
    ),
)