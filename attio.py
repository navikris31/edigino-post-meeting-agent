import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

ATTIO_API_KEY = os.environ.get("ATTIO_API_KEY", "")

def find_company_by_domain(domain: str):
    if not ATTIO_API_KEY:
        return None
        
    headers = {
        "Authorization": f"Bearer {ATTIO_API_KEY}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    url = "https://api.attio.com/v2/objects/companies/records/query"
    payload = {
        "filter": {
            "$or": [
                {"domains": {"$contains": domain}}
            ]
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                # Return the internal record ID
                return data["data"][0]["id"]["record_id"]
    except Exception as e:
        print(f"Attio query failed: {e}")
    return None

def create_note_for_company(record_id: str, content: str):
    headers = {
        "Authorization": f"Bearer {ATTIO_API_KEY}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    url = "https://api.attio.com/v2/notes"
    payload = {
        "data": {
            "parent_object": "companies",
            "parent_record_id": record_id,
            "title": "LLM Meeting Recap & Bottlenecks",
            "content_plaintext": content
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Failed to create Attio note: {e}")
        return False

def route_to_attio(domain: str, intelligence_summary: str) -> bool:
    print(f"Searching Attio for domain: {domain}")
    record_id = find_company_by_domain(domain)
    if record_id:
        print(f"Match found. Creating note for Company Record ID: {record_id}")
        return create_note_for_company(record_id, intelligence_summary)
    else:
        print(f"No match found in Attio for domain: {domain}")
        return False
