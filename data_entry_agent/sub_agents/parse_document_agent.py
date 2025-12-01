
import os
import asyncio
from typing import Any

from PIL import Image
import pdfplumber
import pytesseract

from google.adk.agents import Agent
from google.adk.tools import FunctionTool, ToolContext
from google.adk.models.google_llm import Gemini
from google.genai import types
from .utils import retry_config, logging, GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL

# Simple extractor that prefers local files, falls back to artifacts via ToolContext.
async def extract_file_text(filename: str, tool_context: ToolContext) -> str:
    """Return extracted text from a local file path or a saved artifact. Supports images ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif" (OCR) and PDFs (text extraction + OCR fallback)."""
    # If local file exists, use it
    if os.path.isfile(filename):
        path = filename
    else:
        # attempt to load artifact (ADK ToolContext)
        try:
            artifact = await tool_context.load_artifact(filename=filename)
            if artifact and getattr(artifact, "inline_data", None):
                data = artifact.inline_data.data
                # write to temp file for processing
                import tempfile
                suffix = ".pdf" if artifact.inline_data.mime_type == "application/pdf" else ""
                tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tf.write(data)
                tf.flush()
                tf.close()
                path = tf.name
            else:
                raise FileNotFoundError(f"Artifact '{filename}' not found or empty")
        except Exception as e:
            raise RuntimeError(f"Could not load file '{filename}': {e}")

    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"):
            img = Image.open(path)
            return pytesseract.image_to_string(img)
        elif ext == ".pdf":
            texts = []
            logging.info(f"Extracting text from PDF file at path: {path}")
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text() or ""
                    texts.append(t)
            combined = "\n\n".join(texts).strip()
            if combined:
                return combined
            # fallback to OCR render if no text extracted
            ocr_texts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    pil = page.to_image(resolution=150).original
                    ocr_texts.append(pytesseract.image_to_string(pil))
            return "\n\n".join(ocr_texts).strip()
        else:
            # treat as plain text file
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    finally:
        # if we wrote a temp file from artifact, remove it
        if not os.path.isfile(filename) and 'tf' in locals():
            try:
                os.unlink(tf.name)
            except Exception:
                pass

# Wrap extractor as a FunctionTool so ADK can call it from the agent.
extract_tool = FunctionTool(
    func=extract_file_text,

)



pdf_image_parser_agent = Agent(
    name="pdf_image_parser_agent",
    model=Gemini(model=GEMINI_FLASH_MODEL, retry_options=retry_config),
    instruction=(
        "You are a document parser. When given a filename (local path or artifact name), and a url (if provided), to fill the form "
        #"Only call the extract_file_text tool to extract raw text, then return a JSON object with keys: "
       '"raw_text" and "summary" (2-4 sentence summary). '
       "Do not add explanations. Output only JSON object. "
        'Do not ask the user if would like you to do so. '
        'Do not tell the user that you cannot access urls browser or fill forms even if the user is asking to fill the form. '
        "If the document is empty or cannot be parsed, return an empty JSON object {}."
        "Show the JSON object only as the final output. "
        "Do not add explanations. Output only JSON object. "

        #" your output will be used by another agent to fill the form."
 
    ),
    #tools=[extract_tool],
    output_key="parsed_document",

)

