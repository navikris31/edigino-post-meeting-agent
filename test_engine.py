from engine import process_transcript

test_transcript = "Chris: We need to automate lead scraping. Tomas: Sounds good."

try:
    intel = process_transcript(test_transcript)
    print("SUCCESS!")
    print(intel.summary)
except Exception as e:
    import traceback
    traceback.print_exc()
