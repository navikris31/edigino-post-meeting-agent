import requests
import json

url = "http://localhost:8000/api/webhooks/manual-trigger"

test_data = {
    "meeting_id": "TEST-123456",
    # Set this to a matching domain in your Attio database to test CRM routing,
    # or an unknown domain to test the fallback email.
    "contact_domain": "example.com", 
    "contact_email": "hello@example.com",
    "transcript_text": """
    Chris: Hello Tomas, thanks for joining. Let's talk about Edigino's services.
    Tomas: Hi Chris. Yeah, our current customer acquisition process is very slow. We manually scrape leads from directories, and it takes hours.
    Chris: That's definitely a bottleneck we can fix. We can automate the scraping and connect it directly to your CRM.
    Tomas: That sounds great. Also, we struggle with closing deals; our sales scripts feel a bit generic. Can you overhaul them?
    Chris: Yes, we can completely rewrite your scripts based on your specific value proposition. For next steps, I'll need you to send over your current CRM login details by tomorrow. 
    Tomas: Great, I will do that. When can you send me the proposed new scripts?
    Chris: I will send those to you by April 25th, 2026. The total cost for this quick overhaul will be €1.500.
    Tomas: Perfect. Talk to you soon!
    """
}

print("Sending test request to FastAPI webhook...")
try:
    response = requests.post(url, json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
    print("\nCheck the terminal where FastAPI is running to see the background processing logs!")
except Exception as e:
    print(f"Error: Could not connect to {url}. Is the FastAPI server running?")
