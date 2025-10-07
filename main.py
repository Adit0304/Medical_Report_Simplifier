import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException

from pipeline.ocr_extractor import extract_text_from_image
from pipeline.llm_processor import process_text_with_llm
from pipeline.validator import validate_llm_output

# Initialize FastAPI App
app = FastAPI(
    title="AI Medical Report Simplifier",
    description="Upload a scanned medical report to extract, normalize, and simplify the findings.",
    version="2.1.0"
)

@app.post("/simplify_report/")
async def simplify_medical_report(file: UploadFile = File(...)):
    """
    This endpoint orchestrates the pipeline:
    1. Extracts text from the uploaded image using OCR.
    2. Processes the text with an LLM for normalization and summarization.
    3. Validates the LLM output to prevent hallucinations.
    4. Returns the final, patient-friendly JSON output.
    """
    # Step 1: OCR / Text Extraction
    ocr_text = await extract_text_from_image(file)
    
    # Step 2 & 3: Normalization and Summarization using LLM
    llm_output_json = await process_text_with_llm(ocr_text)
    
    # Step 4: Guardrail / Validation
    validate_llm_output(llm_output_json, ocr_text)
    
    # Step 5: Final Output
    final_output = {
        "tests": llm_output_json.get("tests", []),
        "summary": llm_output_json.get("summary", ""),
        "explanations": llm_output_json.get("explanations", []),
        "status": "ok"
    }

    return final_output

if __name__ == "__main__":
    # To run this service:
    # 1. Ensure you have Tesseract OCR installed and configured.
    # 2. Set your GEMINI_API_KEY environment variable.
    # 3. Install dependencies: pip install "fastapi[all]" Pillow pytesseract google-generativeai python-multipart
    # 4. Run the server: uvicorn main:app --reload
    #
    # The API will be available at http://127.0.0.1:8000/docs for testing.
    uvicorn.run(app, host="0.0.0.0", port=8000)
