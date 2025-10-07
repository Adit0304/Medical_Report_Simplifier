from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Define the structure for a single test result, which will be used in the final output
class TestResult(BaseModel):
    name: str
    value: float
    unit: str
    status: str
    ref_range: Optional[Dict[str, float]] = None

# Define the final output structure that the validator will produce.
# This resolves the ImportError in validator.py.
class FinalOutput(BaseModel):
    tests: List[TestResult]
    summary: str
    status: str = "ok"

# This is the schema for the LLM's expected JSON output.
# The LLM is not expected to produce the top-level 'status' field.
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "tests": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "number"},
                    "unit": {"type": "string"},
                    "status": {"type": "string", "enum": ["low", "high", "normal"]},
                    "ref_range": {
                        "type": "object",
                        "properties": {
                            "low": {"type": "number"},
                            "high": {"type": "number"}
                        },
                    }
                },
                "required": ["name", "value", "unit", "status"]
            }
        },
        "summary": {"type": "string"},
        "explanations": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["tests", "summary", "explanations"]
}

