import difflib
from fastapi import HTTPException
from .schemas import FinalOutput, TestResult
from typing import List

def validate_llm_output(llm_response: dict, ocr_text: str) -> FinalOutput:
    """
    Validates the LLM's output, filtering out any tests that cannot be verified
    against the source text instead of failing the entire request.
    """
    processed_tests = llm_response.get("tests", [])
    ocr_words = ocr_text.lower().split()

    valid_tests: List[TestResult] = []
    dropped_tests: List[str] = []

    # Iterate through each test and validate it
    for test_data in processed_tests:
        test = TestResult(**test_data)
        test_name = test.name
        
        if test_name:
            # Use fuzzy matching to find the test name in the OCR text.
            # A cutoff of 0.8 requires a high degree of similarity.
            matches = difflib.get_close_matches(test_name.lower(), ocr_words, n=1, cutoff=0.8)
            
            if matches:
                # If a close match is found, the test is valid.
                valid_tests.append(test)
            else:
                # If no match is found, add it to the dropped list.
                dropped_tests.append(test_name)

    # Prepare warnings if any tests were dropped
    warnings = []
    if dropped_tests:
        warning_message = (
            "Guardrail triggered: The following tests were excluded because they could not be "
            f"verified against the source report: {', '.join(dropped_tests)}"
        )
        warnings.append(warning_message)

    # Structure the final output with valid tests and any warnings
    final_output = FinalOutput(
        tests=valid_tests,
        summary=llm_response.get("summary", ""),
        warnings=warnings if warnings else None,
        status="ok"
    )
    
    return final_output



# import difflib
# from fastapi import HTTPException
# from .schemas import FinalOutput

# def validate_llm_output(llm_response: dict, ocr_text: str) -> FinalOutput:
#     """
#     Validates the LLM's output against the original OCR text to prevent hallucinations
#     using fuzzy string matching to account for spelling variations and OCR errors.
#     """
#     processed_tests = llm_response.get("tests", [])
#     # Split the OCR text into a list of individual words for comparison.
#     ocr_words = ocr_text.split()

#     # Guardrail: Check for hallucinated tests
#     for test in processed_tests:
#         test_name = test.get("name")
#         if test_name:
#             # Use difflib to find close matches for the test name within the OCR text.
#             # This is case-insensitive by default when possibilities are lowercased.
#             # A cutoff of 0.8 requires a high degree of similarity.
#             # If get_close_matches returns an empty list, no sufficiently similar word was found.
#             matches = difflib.get_close_matches(test_name, ocr_words, n=1, cutoff=0.8)
            
#             if not matches:
#                 reason = f"Guardrail triggered: Hallucinated test '{test_name}' not found in the source medical report."
#                 raise HTTPException(status_code=400, detail={"status": "unprocessed", "reason": reason})

#     # If validation passes, structure the final output
#     final_output = FinalOutput(
#         tests=processed_tests,
#         summary=llm_response.get("summary", ""),
#         status="ok"
#     )
    
#     return final_output

