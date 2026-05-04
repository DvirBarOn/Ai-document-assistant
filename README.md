# AI Document Assistant

AI Document Assistant is a lightweight document analysis tool built with Python and Streamlit.

The app allows users to paste text or upload TXT/PDF files, extract document content, and analyze it using AI through the OpenRouter API. If the free AI models are temporarily unavailable or rate-limited, the app provides a local fallback analysis and a manual ChatGPT prompt that can be copied and used with the original document.

## Features

- Paste text manually
- Upload TXT files
- Upload PDF files
- Extract text from uploaded PDF/TXT documents
- Choose analysis type:
  - General Analysis
  - Study Notes
  - Action Items Only
  - Risks / Issues
- Analyze documents using AI via OpenRouter
- Try multiple free AI models before falling back
- Local fallback analysis when AI is unavailable
- Manual ChatGPT prompt fallback for unavailable API models
- Secure API key handling using a `.env` file

## Tech Stack

- Python
- Streamlit
- OpenRouter API
- HTTPX
- PyMuPDF
- python-dotenv

## Project Structure

```text
ai-document-assistant/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

> Note: `.env` is not uploaded to GitHub because it contains the API key.

## Installation

Clone the repository:

```bash
git clone https://github.com/DvirBarOn/Ai-document-assistant.git
cd Ai-document-assistant
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root folder of the project:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Do not share or upload your `.env` file.

## Running the App

Run the Streamlit app:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## How It Works

1. The user pastes text or uploads a TXT/PDF file.
2. The app extracts text from the uploaded document.
3. The user selects an analysis mode.
4. The app builds a structured prompt.
5. The app sends the prompt to OpenRouter.
6. If an AI model responds, the app displays the AI analysis.
7. If the free models are rate-limited, the app shows:
   - Local Analysis
   - Manual ChatGPT Prompt

## Analysis Modes

### General Analysis

Returns:

- Short summary
- Key points
- Action items
- Risks or important notes

### Study Notes

Returns:

- Study summary
- Important concepts
- Step-by-step explanation
- Key formulas or methods
- Practice questions
- Things to remember

### Action Items Only

Extracts:

- Tasks
- Responsibilities
- Deadlines
- Next steps

### Risks / Issues

Extracts:

- Risks
- Problems
- Blockers
- Missing information
- Unclear details
- Concerns

## Fallback Behavior

The app uses free OpenRouter models. These models may sometimes be temporarily rate-limited.

If the AI request fails or the models are unavailable, the app provides:

1. A basic local analysis using Python rules.
2. A manual ChatGPT prompt that the user can copy after uploading the original document to ChatGPT.

This keeps the app usable even when the external AI model is unavailable.

## Limitations

- Free OpenRouter models may be rate-limited.
- Local Analysis is not a true AI analysis.
- Scanned PDFs may not work because OCR is not implemented.
- The app does not store document history.
- The app currently runs locally only.

## Future Improvements

- Add OCR support for scanned PDFs
- Add Excel file support
- Improve the UI design
- Add document history
- Add export to PDF/Markdown/TXT
- Add support for more AI providers
- Add deployment support

## Author

Built by Dvir Bar On as a lightweight AI document analysis project.