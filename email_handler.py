import os
import imaplib
import time
from email.message import EmailMessage
from email.utils import formatdate
from dotenv import load_dotenv

load_dotenv(override=True)

IMAP_SERVER = os.environ.get("HOSTINGER_IMAP_SERVER", "imap.hostinger.com")
IMAP_PORT = int(os.environ.get("HOSTINGER_IMAP_PORT", "993"))
EMAIL = os.environ.get("AGENT_EMAIL", "sales@edigino.com")
PASSWORD = os.environ.get("AGENT_EMAIL_PASSWORD", "")
FALLBACK_EMAIL = os.environ.get("FALLBACK_EMAIL_TO", "sales@edigino.com")

def convert_to_draft_format(recipient: str, subject: str, html_body: str) -> bytes:
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = recipient
    msg['Date'] = formatdate(localtime=True)
    msg.set_content(html_body, subtype='html')
    return bytes(msg)

def save_draft(to_email: str, subject: str, html_content: str) -> bool:
    """Logs into Hostinger via IMAP and APPENDS the email to the Drafts folder."""
    if not PASSWORD:
        print("AGENT_EMAIL_PASSWORD not set. Logging to console instead.")
        print(f"DRAFT TO: {to_email}\nSUBJECT: {subject}\n{html_content}\n")
        return False
        
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, PASSWORD)
        
        # Format message
        msg_bytes = convert_to_draft_format(to_email, subject, html_content)
        
        # 'Drafts' is the standard folder for Hostinger, may require 'INBOX.Drafts' depending on user settings
        append_status, _ = mail.append(
            'INBOX.Drafts', 
            '(\\Draft)', 
            imaplib.Time2Internaldate(time.time()), 
            msg_bytes
        )
        mail.logout()
        
        return append_status == 'OK'
    except Exception as e:
        print(f"Failed to save draft via IMAP: {e}")
        return False

def send_fallback_email(subject: str, text_content: str):
    """
    Creates an [ACTION REQUIRED] Orphaned Meeting Recap draft if Attio math fails.
    """
    subject_line = f"[ACTION REQUIRED] Orphaned Meeting Recap - {subject}"
    html_content = text_content.replace('\n', '<br>')
    return save_draft(FALLBACK_EMAIL, subject_line, html_content)
