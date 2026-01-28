import os
import requests
import json

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: GEMINI_API_KEY not set.")
    exit()

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

try:
    response = requests.get(url)
    data = response.json()
    
    if 'models' in data:
        print(f"{'MODEL ID':<30} | {'DISPLAY NAME'}")
        print("-" * 50)
        for model in data['models']:
            # Filter for models that support content generation
            if "generateContent" in model.get("supportedGenerationMethods", []):
                # Clean up the ID (remove 'models/' prefix if present)
                model_id = model['name'].replace("models/", "")
                print(f"{model_id:<30} | {model.get('displayName')}")
    else:
        print("Error listing models:", data)

except Exception as e:
    print(f"Connection failed: {e}")