# Trust KYC Autofill (Individual)

Small FastAPI application that extracts KYC data from uploaded documents, normalises
it into a structured `ClientProfile`, and renders question/answer lists for the
forms used by our Hong Kong trust company:

- 1.3 客户开户申请表（个人）
- 1.4 Declaration on Source of Wealth – Individual
- 1.5 无犯罪、监管、制裁或罚款声明（个人）
- 1.2 CRS Individual Self Certification Form
- 1.1 Form W-8BEN (individual)

## Project layout

```
trust-kyc-autofill-individual/
  backend/
    main.py            # FastAPI app
    models.py          # Pydantic data structures
    openai_client.py   # Wrapper around OpenAI Responses API
    templates.py       # Maps ClientProfile fields into form answers
    text_extractor.py  # PDF / Word / image extraction utilities
    requirements.txt
  frontend/
    index.html
    app.js
    styles.css
```

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
uvicorn backend.main:app --reload
```

The server exposes:

- `POST /api/extract` – upload a document and receive the plain text.
- `POST /api/generate` – send free-form text and receive a `ClientProfile` with
  mapped form answers.
- `POST /api/process` – upload once and run both extraction + generation.

## Frontend

The static files in `frontend/` can be served with any HTTP server (e.g. `python -m http.server`).
Set `API_BASE` in `app.js` if the backend is hosted elsewhere.

## Notes

- Text extraction relies on `PyPDF2`, `docx2txt`, and `pytesseract`. Install the
  Tesseract binary if image OCR is required.
- OpenAI integration uses the [Responses API](https://platform.openai.com/docs/guides/responses/response-formats)
  with `ClientProfile` schema enforcement for deterministic JSON output.
