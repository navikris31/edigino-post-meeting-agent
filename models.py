from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class MeetingEvent(BaseModel):
    meeting_id: str
    contact_email: Optional[str] = None
    contact_domain: Optional[str] = None
    transcript_text: str
    
class ActionItem(BaseModel):
    task: str
    assignee: str # "Edigino" or "Client"
    deadline: Optional[str] = None

class MeetingIntelligence(BaseModel):
    summary: str
    problems_to_solutions: List[Dict[str, str]] # e.g., [{"problem": "...", "solution": "..."}]
    bottlenecks: List[str]
    edigino_homework: List[ActionItem]
    client_homework: List[ActionItem]
    timeline_next_steps: str
    email_draft_lt: str
