import os
import glob
import google.generativeai as genai
from models import MeetingIntelligence
from dotenv import load_dotenv
import json

load_dotenv(override=True)

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "NOT_SET"))

def load_reference_emails(folder_path: str = "data/reference_emails") -> str:
    """Loads all text files from the reference emails folder as a single string."""
    emails = []
    if os.path.exists(folder_path):
        for filepath in glob.glob(f"{folder_path}/*.txt"):
            with open(filepath, 'r', encoding='utf-8') as f:
                emails.append(f.read())
    return "\n\n---\n\n".join(emails)

def process_transcript(transcript: str) -> MeetingIntelligence:
    """Processes the transcript using Gemini to extract intelligence and draft emails."""
    
    reference_emails = load_reference_emails()
    
    prompt = f"""
    You are the Edigino Sales Operations Agent. Your task is to process a meeting transcript and extract structured intelligence.

    ### 1. Identify Discussion & Bottlenecks
    - Map Current Problems -> Proposed Solutions.
    - CRITICAL: Identify EVERY bottleneck in the client's processes. Document technical hurdles, workflow gaps, and operational friction points in detail. Do not miss any detail.

    ### 2. Action Items
    - Separate "Edigino Homework" from "Client Homework".

    ### 3. Timeline
    - Summarize next steps and scheduled dates.

    ### 4. Communication (Lithuanian Draft)
    - Draft an email addressing the recap, identified bottlenecks, and homework.
    - Language: STRICTLY LITHUANIAN.
    - Tone: Mimic the strict brand voice found in the reference emails provided below.
    - Formatting: Use European standards (e.g., €1.500, YYYY-MM-DD).

    ### Reference Emails for Tone Matching:
    {reference_emails}

    ### Raw Meeting Transcript:
    {transcript}

    Respond ONLY with a valid JSON object matching this schema precisely:
    {{
      "summary": "High level summary",
      "problems_to_solutions": [{{"problem": "...", "solution": "..."}}],
      "bottlenecks": ["bottleneck 1", "bottleneck 2"],
      "edigino_homework": [{{"task": "...", "assignee": "Edigino", "deadline": "YYYY-MM-DD"}}],
      "client_homework": [{{"task": "...", "assignee": "Client", "deadline": "YYYY-MM-DD"}}],
      "timeline_next_steps": "Detailed timeline",
      "email_draft_lt": "Sveiki, ..."
    }}
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    # Use JSON mode if supported, or standard generation
    generation_config = {"response_mime_type": "application/json"}
    
    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        data = json.loads(response.text)
        return MeetingIntelligence(**data)
    except Exception as api_err:
        print(f"\\n[!] Gemini API failed ({api_err}).")
        raise RuntimeError(f"Failed to generate valid Meeting Intelligence: {api_err}")
