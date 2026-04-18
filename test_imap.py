import os
import imaplib
from dotenv import load_dotenv

load_dotenv()

IMAP_SERVER = os.environ.get("HOSTINGER_IMAP_SERVER", "imap.hostinger.com")
IMAP_PORT = int(os.environ.get("HOSTINGER_IMAP_PORT", "993"))
EMAIL = os.environ.get("AGENT_EMAIL", "")
PASSWORD = os.environ.get("AGENT_EMAIL_PASSWORD", "")

def check_folders():
    if not PASSWORD:
        print("Error: Password not found in .env")
        return

    print(f"Connecting to {IMAP_SERVER}:{IMAP_PORT} as {EMAIL}...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, PASSWORD)
        print("Login successful!")
        
        status, folders = mail.list()
        print("Available folders:")
        for folder in folders:
            print(f"- {folder.decode('utf-8')}")
            
        mail.logout()
    except Exception as e:
        print(f"IMAP Error: {e}")

if __name__ == "__main__":
    check_folders()
