from fastapi import FastAPI, BackgroundTasks, HTTPException
from typing import Optional, Dict, Any
from pydantic import BaseModel
import uvicorn
import json

from models import MeetingEvent
from engine import process_transcript
from attio import route_to_attio
from email_handler import save_draft, send_fallback_email

app = FastAPI(title="Edigino Sales Operations Agent")

def generate_recap_text(intel) -> str:
    """Formats the meeting intelligence into a readable text recap for CRM/Fallback."""
    lines = []
    lines.append(f"Summary: {intel.summary}")
    lines.append("\n=== Bottlenecks ===")
    for b in intel.bottlenecks:
        lines.append(f"- {b}")
    lines.append("\n=== Problems to Solutions ===")
    for mapping in intel.problems_to_solutions:
        lines.append(f"- Problem: {mapping.get('problem')} -> Solution: {mapping.get('solution')}")
    lines.append("\n=== Edigino Homework ===")
    for item in intel.edigino_homework:
        lines.append(f"- {item.task} (Deadline: {item.deadline})")
    lines.append("\n=== Client Homework ===")
    for item in intel.client_homework:
        lines.append(f"- {item.task} (Deadline: {item.deadline})")
    lines.append(f"\nTimeline / Next Steps: {intel.timeline_next_steps}")
    
    return "\n".join(lines)


def process_meeting_background(event: MeetingEvent):
    """The central orchestration function executed in the background."""
    print(f"Starting processing for meeting: {event.meeting_id}")
    
    # 1. Process via Gemini Engine
    intel = process_transcript(event.transcript_text)
    print("Intelligence extracted successfully.")
    
    recap_text = generate_recap_text(intel)
    
    # 2. Smart CRM Routing (Attio)
    crm_matched = False
    if event.contact_domain:
        crm_matched = route_to_attio(event.contact_domain, recap_text)
    
    # 3. Handle Fallback if CRM missing
    if not crm_matched:
        print("Attio mapping failed or absent, routing to fallback email.")
        send_fallback_email(f"Meeting {event.meeting_id}", recap_text)
        
    # 4. Create Communication Draft (Lithuanian)
    print("Saving Lithuanian email draft...")
    recipient = event.contact_email if event.contact_email else "unknown@client.com"
    subject = "Po mūsų susitikimo – kitų žingsnių planas"
    formatted_draft = intel.email_draft_lt.replace('\n', '<br>')
    
    save_draft(recipient, subject, formatted_draft)
    print("Workflow completed.")


@app.post("/api/webhooks/post-meeting")
async def handle_post_meeting_webhook(event: MeetingEvent, background_tasks: BackgroundTasks):
    """
    Primary trigger: Receives transcript automatically from Gemini Notetaker.
    """
    if not event.transcript_text:
        raise HTTPException(status_code=400, detail="Transcript is required.")
        
    background_tasks.add_task(process_meeting_background, event)
    return {"status": "Processing scheduled", "meeting_id": event.meeting_id}


@app.post("/api/webhooks/manual-trigger")
async def handle_manual_trigger(event: MeetingEvent, background_tasks: BackgroundTasks):
    """
    Manual override trigger for Chrome extension.
    """
    if not event.transcript_text:
        raise HTTPException(status_code=400, detail="Transcript is required.")
        
    background_tasks.add_task(process_meeting_background, event)
    return {"status": "Manual processing scheduled", "meeting_id": event.meeting_id}


@app.post("/api/webhooks/krisp")
async def handle_krisp_honeypot(payload: Dict[str, Any]):
    """
    Honeypot endpoint to capture Krisp's native webhook JSON payload.
    It simply prints the entire JSON to the terminal for us to study.
    """
    print("\\n" + "="*50)
    print("🚨 KRISP WEBHOOK INTERCEPTED 🚨")
    print(json.dumps(payload, indent=2))
    print("="*50 + "\\n")
    return {"status": "Krisp payload received and logged successfully!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
