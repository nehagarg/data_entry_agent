# data_entry_agent
This agent helps you fill web forms by parsing the information from the document uploaded by you.

## Prerequisites
- Python 3.11+ (project uses 3.11 in dev environment)
- Node.js + npm (to run Playwright MCP server)
- (Optional) Tesseract OCR binary if you will parse images/PDFs via OCR
- Environment variables (set in .env):
  - `GOOGLE_API_KEY` — provide your GOOGLE_API_KEY in .env file

## Setup (recommended)
1. Create & activate a virtualenv:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install Python dependencies (adjust if you have a requirements file):
   ```bash
   pip install google-adk google-genai playwright pdfplumber pillow pytesseract
   # install Playwright browsers (if running Playwright locally)
   npx playwright install
   ```

3. Start Playwright MCP server (example uses port `8931`):
   ```bash
   npx @playwright/mcp@latest --port 8931 --save-trace --output-dir <output-dir path to save debug traces>
   ```

## Run the agent
Clone this repo into a root folder.
Run this from the root folder containing data_entry_agent folder
```bash
adk web --log_level DEBUG
```
You can change the log_level to INFO if you do not wish to see the detailed logs.


## Where to look in this repo
- Main agent: `data_entry_agent/agent.py`
- Browser Interaction agent: `data_entry_agent/sub_agents/fill_form_mcp_agent.py`
- PDF/image parser agent: `data_entry_agent/sub_agents/parse_document_agent.py`
