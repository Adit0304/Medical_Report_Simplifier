import os
import json
import asyncio
import google.generativeai as genai
from fastapi import HTTPException
from dotenv import load_dotenv
from .schemas import JSON_SCHEMA

# Load environment variables from a .env file
load_dotenv()

# --- Configuration ---
try:
    # Use .get() for safer access to the environment variable.
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("The GEMINI_API_KEY environment variable has not been set.")
    genai.configure(api_key=api_key)
except (KeyError, ValueError) as e:
    raise Exception(
        "GEMINI_API_KEY not found or is empty. "
        "Please create a .env file and add your key, or set the environment variable."
    ) from e


# --- LLM Configuration ---
generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 1,
    "max_output_tokens": 8192, # Keep the higher token limit
    "response_mime_type": "application/json",
}

# Relax safety settings to prevent false positives with medical text
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]

def build_enhanced_llm_prompt(ocr_text: str) -> str:
    """Creates a more robust and detailed prompt for the LLM."""
    return f"""
    You are an expert medical data processor. Your task is to analyze the following text, which was extracted from a medical report via OCR, and convert it into a structured JSON format according to the provided schema.

    **Critical Instructions:**
    1.  **Error Correction:** The OCR text may contain errors (e.g., "Hemglobin" instead of "Hemoglobin"). Use your medical knowledge to interpret and correct these errors.
    2.  **Data Normalization:** Standardize test names to their most common clinical representation found within the source text. For an initialism like "WBC", the 'name' field in your output should also be "WBC".
    3.  **Infer and Determine Status:** Based on standard medical reference ranges, accurately determine if each test result is "low", "high", or "normal". Use your internal knowledge if no range is provided in the text.
    4.  **Patient-Friendly Summarization:** Create a single, concise summary paragraph. This summary should mention the key findings (especially abnormal results) and briefly explain what they might generally indicate (e.g., "A high White Blood Cell count can occur with infections.").
    5.  **Strict Adherence to Source:** You MUST NOT include any test in your output that is not mentioned or clearly implied in the OCR text. Do not hallucinate data.
    6.  **JSON Output:** Format the final output as a single, valid JSON object that strictly matches the provided schema. Do not include a separate 'explanations' list; integrate all explanations into the 'summary' text.

    **OCR Text to Process:**
    ---
    {ocr_text}
    ---
    """

async def process_text_with_llm(ocr_text: str):
    """
    Sends the OCR text to the Gemini model and gets the structured output.
    """
    model = genai.GenerativeModel(
        model_name="models/gemini-2.5-flash",
        generation_config={**generation_config, "response_schema": JSON_SCHEMA},
        safety_settings=safety_settings
    )
    prompt = build_enhanced_llm_prompt(ocr_text)
    
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        return json.loads(response.text)
    except Exception as e:
        error_message = f"Failed to process the report with the AI model: {e}"
        # Check for specific finish reasons in the error message if available
        if hasattr(e, 'message'):
            if "Finish Reason: SAFETY" in e.message:
                error_message = "Failed to process the report: The response was blocked by safety filters."
            elif "Finish Reason: MAX_TOKENS" in e.message:
                error_message = "Failed to process the report: The AI's response was too long and was cut off."
        
        print(f"Error during Gemini API call: {e}")
        raise HTTPException(status_code=500, detail=error_message)

