# Medical Report Simplifier

**AI-powered API to extract, normalize, and simplify findings from scanned medical reports.**

---

## 📁 Project Structure

```
Medical_Report_Simplifier/
├── .gitignore
├── main.py
├── requirements.txt
└── pipeline/
    ├── llm_processor.py
    ├── ocr_extractor.py
    ├── schemas.py
    └── validator.py
```

- **main.py**: FastAPI entrypoint and endpoint orchestration.
- **pipeline/**
  - **ocr_extractor.py**: OCR extraction from uploaded images.
  - **llm_processor.py**: LLM prompt building and Gemini API integration.
  - **schemas.py**: Pydantic models and JSON schema for validation.
  - **validator.py**: Guardrails to prevent hallucinated test results.

---

## ✨ Features

- **OCR Extraction**: Converts scanned medical report images to text.
- **LLM Normalization**: Uses Gemini AI to standardize and summarize findings.
- **Guardrails**: Validates LLM output against source text to prevent hallucinations.
- **Patient-Friendly Output**: Returns structured, easy-to-understand JSON.
- **FastAPI**: Interactive API docs and easy integration.

---

## 🚀 Installation

1. **Clone the repository**
   ```sh
   git clone <your-repo-url>
   cd Medical_Report_Simplifier
   ```

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**
   - [Windows](https://github.com/tesseract-ocr/tesseract/wiki)
   - [macOS](https://tesseract-ocr.github.io/tessdoc/Installation.html)
   - [Linux](https://tesseract-ocr.github.io/tessdoc/Installation.html)

4. **Set up environment variables**
   - Create a `.env` file:
     ```
     GEMINI_API_KEY=your_google_gemini_api_key
     ```

5. **Run the API server**
   ```sh
   uvicorn main:app --reload
   ```

---

## 🛠️ API Endpoints

### `POST /simplify_report/`

**Description:**  
Upload a scanned medical report image to receive a simplified, structured JSON output.

**Request:**
- `file`: Image file (PNG, JPG, etc.)

**Response:**
```json
{
  "tests": [
    {
      "name": "Hemoglobin",
      "value": 13.5,
      "unit": "g/dL",
      "status": "normal",
      "ref_range": {"low": 12.0, "high": 16.0}
    }
    // ...
  ],
  "summary": "Your results are mostly normal. High WBC may indicate infection.",
  "explanations": [
    "A high White Blood Cell count can occur with infections."
  ],
  "status": "ok"
}
```

**Interactive Docs:**  
Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) after starting the server.

---

## 🧑‍⚕️ How It Works

1. **OCR**: Extracts text from uploaded image.
2. **LLM**: Processes text, corrects errors, normalizes test names, summarizes findings.
3. **Validation**: Ensures only verifiable tests are included.
4. **Output**: Returns patient-friendly JSON.

---

## 📄 License

MIT License

---

## 🤝 Contributing

Pull requests and issues are welcome!