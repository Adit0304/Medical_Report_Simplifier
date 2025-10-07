# from fastapi import UploadFile, HTTPException
# from PIL import Image
# import pytesseract
# import asyncio

# async def extract_text_from_image(file: UploadFile) -> str:
#     """
#     Performs OCR on an uploaded image file to extract raw text.
    
#     Args:
#         file: The uploaded image file.

#     Returns:
#         The extracted text as a string.
        
#     Raises:
#         HTTPException: If the file is invalid or OCR fails.
#     """
#     try:
#         # Read image content into memory
#         image_bytes = await file.read()
        
#         # Open the image with Pillow
#         image = Image.open(io.BytesIO(image_bytes))
        
#         # Run Tesseract OCR in a separate thread to avoid blocking the event loop
#         loop = asyncio.get_event_loop()
#         ocr_text = await loop.run_in_executor(
#             None, 
#             lambda: pytesseract.image_to_string(image)
#         )

#         if not ocr_text.strip():
#             raise HTTPException(status_code=400, detail="OCR failed. No text could be extracted from the image.")
            
#         return ocr_text
#     except Exception as e:
#         # Catch potential PIL errors for invalid image formats
#         raise HTTPException(status_code=400, detail=f"Invalid image file or OCR processing error: {e}")


import pytesseract
from PIL import Image
import io
from fastapi import UploadFile

async def extract_text_from_image(file_upload: UploadFile) -> str:
    """
    Extracts text from an uploaded image using Tesseract OCR.
    This version uses a specific Page Segmentation Mode (PSM) for better
    accuracy on single-column medical reports, removing complex pre-processing.
    """
    # First, read the file's content into a bytes object.
    image_bytes = await file_upload.read()

    try:
        image = Image.open(io.BytesIO(image_bytes))

        # Use Page Segmentation Mode 4: "Assume a single column of text of variable sizes."
        # This is often more reliable for report-style documents than the complex
        # contour detection logic, which can fail on clear, single-column images.
        custom_config = r'--oem 3 --psm 4'
        text = pytesseract.image_to_string(image, config=custom_config)

        return text
    except Exception as e:
        raise IOError(f"Tesseract OCR failed to process the image. Error: {e}")

