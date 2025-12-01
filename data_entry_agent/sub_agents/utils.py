from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)


class MCPToolSetWithoutSessionClose(MCPToolset):
    async def close(self):
        print(f"MCPToolSetWithoutSessionClose: close() called, but not closing the session to keep the browser alive.", file=self._errlog)
        logging.info("MCPToolSetWithoutSessionClose: close() called, but not closing the session to keep the browser alive.")
        # Override to do nothing, preventing session closure
         
        pass

# --- State Keys ---
STATE_CURRENT_DOC = "current_response"
STATE_CRITICISM = "correction"
# Define the exact phrase the Critic should use to signal completion
COMPLETION_PHRASE = "No major issues found."
GEMINI_FLASH_MODEL = "gemini-2.5-flash"  # Updated model name
GEMINI_PRO_MODEL = "gemini-2.5-pro"  # Updated model name