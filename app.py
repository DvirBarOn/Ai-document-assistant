import os
import re
from collections import Counter

import fitz
import httpx
import streamlit as st
from dotenv import load_dotenv


# =========================================================
# 1. APP CONFIGURATION
# =========================================================

AI_MODELS = [
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# =========================================================
# 2. LOAD API KEY
# =========================================================

def load_openrouter_api_key():
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

    # Clean common mistakes
    api_key = api_key.strip('"').strip("'")
    api_key = api_key.replace("\ufeff", "").strip()

    if api_key.startswith("Bearer "):
        api_key = api_key.replace("Bearer ", "", 1).strip()

    return api_key


openrouter_api_key = load_openrouter_api_key()


# =========================================================
# 3. PROMPT BUILDING
# =========================================================

def build_prompt(text, analysis_mode):
    if analysis_mode == "General Analysis":
        instructions = """
Please return the analysis in this exact format:

### Short Summary
Write a short summary of the document in 3-5 sentences.

### Key Points
List the most important points from the document.

### Action Items
List any tasks, decisions, responsibilities, deadlines, or next steps mentioned in the document.
If there are no action items, write: "No clear action items found."

### Risks or Important Notes
List any risks, warnings, missing information, concerns, or important details.
"""

    elif analysis_mode == "Study Notes":
        instructions = """
Please return the analysis in this exact format:

### Study Summary
Explain the main topic of the document in a clear and simple way.

### Important Concepts
List and explain the most important concepts from the document.

### Step-by-Step Explanation
Break down the main ideas step by step, as if teaching a student.

### Key Formulas / Methods
List any formulas, methods, algorithms, or procedures mentioned in the document.

### Practice Questions
Create 5 practice questions based on the document.

### Things to Remember
List the most important things to remember for an exam or review.
"""

    elif analysis_mode == "Action Items Only":
        instructions = """
Please return the analysis in this exact format:

### Action Items
List only the tasks, decisions, responsibilities, deadlines, or next steps mentioned in the document.

For each action item, include:
- Task
- Owner, if mentioned
- Deadline, if mentioned

If there are no action items, write: "No clear action items found."
"""

    elif analysis_mode == "Risks / Issues":
        instructions = """
Please return the analysis in this exact format:

### Risks / Issues
List any risks, problems, warnings, blockers, missing information, unclear details, or concerns mentioned in the document.

For each risk or issue, explain:
- What the issue is
- Why it matters
- What should be checked next

If there are no clear risks, write: "No clear risks or issues found."
"""

    else:
        instructions = """
Please summarize the document clearly and extract the most important points.
"""

    prompt = f"""
You are an AI Document Assistant.

Your task is to analyze the document below according to the selected analysis mode.

Analysis mode:
{analysis_mode}

{instructions}

Document:
{text}
"""
    return prompt


def build_manual_file_prompt(analysis_mode):
    if analysis_mode == "General Analysis":
        instructions = """
Please analyze the uploaded document and return:

### Short Summary
Write a short summary of the document in 3-5 sentences.

### Key Points
List the most important points from the document.

### Action Items
List any tasks, decisions, responsibilities, deadlines, or next steps.
If there are no action items, write: "No clear action items found."

### Risks or Important Notes
List any risks, warnings, missing information, concerns, or important details.
"""

    elif analysis_mode == "Study Notes":
        instructions = """
Please analyze the uploaded document as study material and return:

### Study Summary
Explain the main topic clearly and simply.

### Important Concepts
List and explain the most important concepts.

### Step-by-Step Explanation
Break down the main ideas step by step, as if teaching a student.

### Key Formulas / Methods
List formulas, methods, algorithms, or procedures mentioned in the document.

### Practice Questions
Create 5 practice questions based on the document.

### Things to Remember
List the most important things to remember for an exam or review.
"""

    elif analysis_mode == "Action Items Only":
        instructions = """
Please analyze the uploaded document and return only:

### Action Items

For each action item, include:
- Task
- Owner, if mentioned
- Deadline, if mentioned

If there are no action items, write: "No clear action items found."
"""

    elif analysis_mode == "Risks / Issues":
        instructions = """
Please analyze the uploaded document and return:

### Risks / Issues

For each risk or issue, explain:
- What the issue is
- Why it matters
- What should be checked next

If there are no clear risks, write: "No clear risks or issues found."
"""

    else:
        instructions = """
Please summarize the uploaded document clearly and extract the most important points.
"""

    prompt = f"""
I uploaded a document.

Please analyze the uploaded document according to this analysis mode:

Analysis mode:
{analysis_mode}

{instructions}

Please keep the answer clear, structured, and useful.
"""
    return prompt


# =========================================================
# 4. FILE READING FUNCTIONS
# =========================================================

def read_txt_file(uploaded_file):
    file_content = uploaded_file.getvalue()
    text = file_content.decode("utf-8")
    return text


def read_pdf_file(uploaded_file):
    file_content = uploaded_file.getvalue()

    pdf_document = fitz.open(
        stream=file_content,
        filetype="pdf"
    )

    text = ""

    for page in pdf_document:
        page_text = page.get_text()
        text += page_text + "\n"

    pdf_document.close()

    return text


def read_uploaded_file(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".txt"):
        return read_txt_file(uploaded_file)

    if file_name.endswith(".pdf"):
        return read_pdf_file(uploaded_file)

    return ""


# =========================================================
# 5. LOCAL ANALYSIS FALLBACK
# =========================================================

def split_into_sentences(text):
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)

    clean_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence) > 20:
            clean_sentences.append(sentence)

    return clean_sentences


def find_possible_action_items(sentences):
    action_keywords = [
        "will",
        "should",
        "needs to",
        "need to",
        "must",
        "next step",
        "deadline",
        "by sunday",
        "by monday",
        "prepare",
        "review",
        "collect",
        "create",
        "build",
        "decided",

        "צריך",
        "צריכה",
        "צריכים",
        "נדרש",
        "נדרשת",
        "יש לבצע",
        "השלב הבא",
        "להכין",
        "לבנות",
        "לאסוף",
        "לבדוק",
        "להגיש",
        "עד",
    ]

    action_items = []

    for sentence in sentences:
        lower_sentence = sentence.lower()

        for keyword in action_keywords:
            if keyword in lower_sentence:
                action_items.append(sentence)
                break

    return action_items[:8]


def find_possible_risks(sentences):
    risk_keywords = [
        "risk",
        "concern",
        "problem",
        "issue",
        "warning",
        "missing",
        "unclear",
        "incomplete",
        "slow",
        "failed",
        "error",

        "סיכון",
        "חשש",
        "בעיה",
        "תקלה",
        "שגיאה",
        "חסר",
        "לא ברור",
        "לא תקין",
        "איטי",
        "קושי",
    ]

    risks = []

    for sentence in sentences:
        lower_sentence = sentence.lower()

        for keyword in risk_keywords:
            if keyword in lower_sentence:
                risks.append(sentence)
                break

    return risks[:8]


def find_common_terms(text):
    words = re.findall(r"[A-Za-zא-ת]{3,}", text.lower())

    stop_words = {
        "the", "and", "for", "that", "this", "with", "from", "are", "was",
        "were", "will", "have", "has", "not", "but", "you", "your", "can",
        "into", "about", "there", "their", "they", "using", "document",

        "של", "על", "עם", "את", "זה", "היא", "הוא", "יש", "לא", "או",
        "אם", "גם", "כל", "כי", "ניתן", "ידי", "כדי", "הזה", "זאת",
        "הם", "הן", "היה", "היתה", "היו", "בין",
    }

    filtered_words = []

    for word in words:
        if word not in stop_words:
            filtered_words.append(word)

    most_common = Counter(filtered_words).most_common(10)

    return most_common


def local_analysis(text, analysis_mode):
    word_count = len(text.split())
    character_count = len(text)
    sentences = split_into_sentences(text)

    action_items = find_possible_action_items(sentences)
    risks = find_possible_risks(sentences)
    common_terms = find_common_terms(text)

    preview = text[:700]

    result = f"""
### Local Analysis

The AI model was not available, so the app created a basic local analysis using Python rules.

### Selected Mode
{analysis_mode}

### Basic Document Info
- Word count: {word_count}
- Character count: {character_count}
- Estimated sentence count: {len(sentences)}
"""

    if analysis_mode in ["General Analysis", "Action Items Only"]:
        result += "\n### Possible Action Items\n"

        if action_items:
            for item in action_items:
                result += f"- {item}\n"
        else:
            result += "- No clear action items found by the local analyzer.\n"

    if analysis_mode in ["General Analysis", "Risks / Issues"]:
        result += "\n### Possible Risks or Important Notes\n"

        if risks:
            for risk in risks:
                result += f"- {risk}\n"
        else:
            result += "- No clear risks found by the local analyzer.\n"

    if analysis_mode in ["General Analysis", "Study Notes"]:
        result += "\n### Repeated Important Terms\n"

        if common_terms:
            for word, count in common_terms:
                result += f"- {word}: {count}\n"
        else:
            result += "- No repeated terms found.\n"

    if analysis_mode == "Study Notes":
        result += """
### Study Notes Reminder
This local mode cannot truly explain concepts like an AI model.
Use the manual ChatGPT prompt below for a better study explanation.
"""

    result += f"""

### Text Preview
{preview}
"""

    return result


# =========================================================
# 6. MANUAL CHATGPT PROMPT FALLBACK
# =========================================================

def show_manual_chatgpt_prompt(analysis_mode):
    file_prompt = build_manual_file_prompt(analysis_mode)

    st.subheader("Manual ChatGPT Prompt")

    st.write(
        "OpenRouter is currently unavailable or rate-limited. "
        "You can continue manually by uploading the original document to ChatGPT "
        "and copying the instruction below."
    )

    st.markdown("### How to use it manually")

    st.write("1. Upload the original PDF/TXT file to ChatGPT.")
    st.write("2. Copy the instruction below.")
    st.write("3. Paste it in ChatGPT after the file is uploaded.")

    st.text_area(
        "Copy this instruction prompt to ChatGPT:",
        value=file_prompt,
        height=300
    )


# =========================================================
# 7. AI REQUEST FUNCTION
# =========================================================

def analyze_document_with_ai(text, analysis_mode):
    prompt = build_prompt(text, analysis_mode)

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "AI Document Assistant",
    }

    for model_name in AI_MODELS:
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        response = httpx.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code == 200:
            data = response.json()

            answer = data["choices"][0]["message"]["content"]

            if not answer:
                return "The model did not return any content."

            return answer

        if response.status_code == 429:
            continue

        raise Exception("OpenRouter request failed.")

    return None


# =========================================================
# 8. STREAMLIT USER INTERFACE
# =========================================================

st.title("AI Document Assistant")

if not openrouter_api_key:
    st.error("OPENROUTER_API_KEY was not found. Check your .env file.")
    st.stop()

st.success("OpenRouter API key loaded successfully.")

st.write("Paste a document, or upload a TXT/PDF file, and the assistant will analyze it.")

analysis_mode = st.selectbox(
    "Choose analysis type:",
    [
        "General Analysis",
        "Study Notes",
        "Action Items Only",
        "Risks / Issues",
    ]
)

uploaded_file = st.file_uploader(
    "Upload a TXT or PDF file",
    type=["txt", "pdf"]
)

pasted_text = st.text_area("Or paste your document text here:")

document_text = ""


# =========================================================
# 9. CHOOSE DOCUMENT SOURCE
# =========================================================

if uploaded_file is not None:
    try:
        document_text = read_uploaded_file(uploaded_file)

        if document_text.strip():
            st.subheader("Uploaded File Preview")
            st.text_area(
                "Content extracted from uploaded file:",
                value=document_text[:1500],
                height=300,
                disabled=True
            )
        else:
            st.warning(
                "The file was uploaded, but no readable text was found. "
                "If this is a scanned PDF, text extraction may not work yet."
            )

    except UnicodeDecodeError:
        st.error("Could not read this TXT file. Please make sure it is saved as UTF-8 text.")
        document_text = ""

    except Exception:
        st.error("Could not read this file. Please try another TXT or PDF file.")
        document_text = ""

elif pasted_text:
    document_text = pasted_text


# =========================================================
# 10. ANALYZE BUTTON LOGIC
# =========================================================

analyze_button = st.button("Analyze Document")

if analyze_button:
    cleaned_text = document_text.strip()

    if cleaned_text:
        try:
            with st.spinner("Analyzing document with OpenRouter AI..."):
                analysis_result = analyze_document_with_ai(cleaned_text, analysis_mode)

            if analysis_result is None:
                st.warning(
                    "All free AI models are temporarily rate-limited. "
                    "Showing local analysis and a manual ChatGPT prompt instead."
                )

                st.subheader("Local Analysis")
                st.markdown(local_analysis(cleaned_text, analysis_mode))

                show_manual_chatgpt_prompt(analysis_mode)

            else:
                st.subheader("AI Analysis")
                st.markdown(analysis_result)

        except Exception:
            st.warning(
                "Something went wrong while contacting the AI model. "
                "Showing local analysis and a manual ChatGPT prompt instead."
            )

            st.subheader("Local Analysis")
            st.markdown(local_analysis(cleaned_text, analysis_mode))

            show_manual_chatgpt_prompt(analysis_mode)

    else:
        st.warning("Please paste text or upload a TXT/PDF file before analyzing.")