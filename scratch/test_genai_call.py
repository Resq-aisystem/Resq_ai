import os
import sys
from pathlib import Path
from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
client = genai.Client(api_key=api_key)

print("Sending request to Gemini API (gemini-3.6-flash)...")
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Generate a 1-sentence emergency briefing for Puri flood warning.",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "briefing": {"type": "STRING"}
            },
            "required": ["briefing"]
        }
    )
)

print("\n--- GEMINI API RESPONSE RECEIVED ---")
print(response.text)
