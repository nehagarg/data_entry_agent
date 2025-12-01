from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams, StdioServerParameters, SseConnectionParams, StreamableHTTPConnectionParams
from google.genai import types
from google.adk.models.google_llm import Gemini
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest

from typing import Optional, Dict
from playwright.async_api import async_playwright, Error as PlaywrightError
from mcp_use import MCPClient
from .utils import retry_config, MCPToolSetWithoutSessionClose, STATE_CURRENT_DOC, GEMINI_PRO_MODEL, GEMINI_FLASH_MODEL
from .parse_document_agent import extract_tool

#import utils

#logging = utils.logging
#retry_config= utils.retry_config

import logging


logger = logging.getLogger("google_adk." + __name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

my_mcp_toolset= McpToolset(
    connection_params=SseConnectionParams(
                url='http://localhost:8931/sse',  #Playwright running in terminal using command npx @playwright/mcp@latest --port 8931 --save-trace --output-dir ./output_trace 
                
            ),
)
browser_interaction_agent_in_seq= LlmAgent(
    name='playwright_interactor_agent',
    model=Gemini(
        model=GEMINI_FLASH_MODEL,
        retry_options=retry_config
    ),
    instruction=(
        "You are an expert web form filling agent. "
        #"You can use the information at {{parsed_document}} to get the values to fill the form. "
        "You can navigate to web pages and fill forms. "
        " Use the appropriate browser tools. "
        #"You can use the following tools to complete your tasks. "
        #"extract_file_text can be used to extract text from documents to help fill forms. "
        "browser_* tools can be used to interact with the browser. "
        "browser_snapshot can be used to get the current page information before calling browser_fill_form. "
        #"Sometimes user may not specifically ask you to extract information from documents, but you should do so if the user has provided a document. "
        #"If the url is provided by the user, you should navigate to the url to fill the form. "
        "You should fill the form based on the information provided in the {{parsed_document}}. Do not hallucinate any information. "
        "You should only fill the form. Do not submit the form. "
        "If you are not filling the form, please provide the reason why you are not filling the form. "
        "If you need the date in a specific format, please convert it to that format. "
        "If you need to fill a checkbox, please select the reference of the correct checkbox and set it to true. "
                
    ),
    #before_agent_callback=before_agent_callback,
    tools=[my_mcp_toolset
        # MCPToolSetWithoutSessionClose(
        #     connection_params=SseConnectionParams(
        #         url='http://localhost:8931/sse',  #Playwright running in terminal using command npx @playwright/mcp@latest --port 8931 --save-trace --output-dir ./output_trace 
        #         header_provider = dynamic_header_provider
        #     ),
            
        #)
    ],
    output_key=STATE_CURRENT_DOC
)


browser_interaction_agent= LlmAgent(
    name='data_entry_agent',
    model=Gemini(
        model=GEMINI_FLASH_MODEL,
        retry_options=retry_config
    ),
    instruction=(
        "You are an expert web form filling agent. "
        #"You can use the information at {{parsed_document}} to get the values to fill the form. "
        #"You can navigate to web pages and fill forms. "
        #" Use the appropriate browser and data extraction tools. "
        "You can use the following tools to complete your tasks. "
        #"extract_file_text can be used to extract text from documents to help fill forms. "
        "browser_* tools can be used to interact with the browser. "
        "browser_snapshot can be used to get the current page before calling browser_fill_form. "
        #"Sometimes user may not specifically ask you to extract information from documents, but you should do so if the user has provided a document. "
        #"If the url is provided by the user, you should navigate to the url to fill the form. "
        "You should fill the form based on the information extracted from the file provided. Do not hallucinate any information. "
        "You should only fill the form. Do not submit the form. "
        "If you are not filling the form, please provide the reason why you are not filling the form. "
        "If you need the date in a specific format, please convert it to that format. "
        "If you need to fill a checkbox, please select the reference of the correct checkbox and set it to true. "
        " Do not close the browser session after filling the form, as you may need to perform more actions later. "
                
    ),
    #before_agent_callback=before_agent_callback,
    tools=[my_mcp_toolset
        # MCPToolSetWithoutSessionClose(
        #     connection_params=SseConnectionParams(
        #         url='http://localhost:8931/sse',  #Playwright running in terminal using command npx @playwright/mcp@latest --port 8931 --save-trace --output-dir ./output_trace 
        #         header_provider = dynamic_header_provider
        #     ),
            # tool_filter=['browser_navigate', 'browser_screenshot', 'browser_fill', 'browser_click']
        #)
    ],
    output_key=STATE_CURRENT_DOC
)
