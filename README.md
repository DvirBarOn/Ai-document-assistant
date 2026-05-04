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
- Manual ChatGPT prompt fallback for long documents or unavailable API models
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