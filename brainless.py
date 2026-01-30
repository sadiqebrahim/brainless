# import sys
# import subprocess
# import os
# import requests
# import json
# import distro # pip install distro

# # --- CONFIGURATION ---
# # "local" for Ollama, "api" for Gemini/OpenAI
# # MODE = "local"
# MODE = "api" 

# # OLLAMA SETTINGS
# OLLAMA_URL = "http://localhost:11434/api/generate"
# OLLAMA_MODEL = "llama3.1" #"mistral"  or "llama3", "codellama"

# # GEMINI SETTINGS
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# def get_system_context():
#     """Returns OS and Shell info for better debugging"""
#     if os.name == 'nt':
#         os_name = "Windows " + os.environ.get('OS', '')
#     else:
#         os_name = distro.name(pretty=True)
#     return f"{os_name} | Shell: {os.path.split(os.environ.get('SHELL', 'unknown'))[-1]}"

# def ask_local_ollama(prompt):
#     """Queries your local Ollama server"""
#     payload = {
#         "model": OLLAMA_MODEL,
#         "prompt": prompt,
#         "stream": False
#     }
#     try:
#         response = requests.post(OLLAMA_URL, json=payload)
#         return response.json().get('response', 'Error: No response from Ollama.')
#     except Exception as e:
#         return f"Error connecting to Ollama: {e}. Is 'ollama serve' running?"

# def ask_gemini(prompt):
#     """Queries Google Gemini API with error handling"""
#     if not GEMINI_API_KEY:
#         return "Error: GEMINI_API_KEY not set."
    
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"
#     headers = {'Content-Type': 'application/json'}
#     data = {"contents": [{"parts": [{"text": prompt}]}]}
    
#     try:
#         response = requests.post(url, headers=headers, json=data)
#         response_data = response.json()

#         # Check if the API returned an error specifically
#         if 'error' in response_data:
#             return f"API Error: {response_data['error'].get('message', 'Unknown error')}"

#         # Check if the model blocked the response (Safety Filters)
#         if 'promptFeedback' in response_data and response_data.get('candidates') is None:
#             return "Error: The prompt was blocked by safety filters."

#         # Valid response
#         if 'candidates' in response_data and response_data['candidates']:
#             return response_data['candidates'][0]['content']['parts'][0]['text']
#         else:
#             return f"Error: Unexpected response format. Raw: {response_data}"

#     except Exception as e:
#         return f"Connection Error: {e}"

# def main():
#     if len(sys.argv) < 2:
#         print("Usage: python brainless.py <command_to_debug>")
#         sys.exit(1)

#     # 1. Get the last command that failed
#     last_command = " ".join(sys.argv[1:])
    
#     print(f"\n🔍 Analyzing: '{last_command}'...")

#     # 2. Re-run it to capture stderr (SAFE MODE: Interactive commands like 'vim' might hang here)
#     # We use a timeout to prevent hanging.
#     try:
#         process = subprocess.run(
#             last_command, 
#             shell=True, 
#             stdout=subprocess.PIPE, 
#             stderr=subprocess.PIPE, 
#             text=True, 
#             timeout=10 # safety timeout
#         )
#         error_log = process.stderr + process.stdout
#     except subprocess.TimeoutExpired:
#         error_log = "Command timed out. It might be waiting for input."
#     except Exception as e:
#         error_log = str(e)

#     if not error_log.strip():
#         print("✅ command ran successfully or produced no output. Nothing to debug.")
#         sys.exit(0)

#     # 3. Construct the prompt
#     context = get_system_context()
#     prompt = f"""
#     You are a CLI terminal assistant. The user ran a command on {context} and it failed.
    
#     COMMAND: {last_command}
#     ERROR OUTPUT:
#     {error_log[-2000:]} 
    
#     Analyze the error. Provide a concise explanation and a specific SHELL COMMAND to fix it.
#     If multiple steps are needed, list them. Be brief.
#     """

#     # 4. Route to the chosen AI
#     if MODE == "local":
#         print(f"🧠 Thinking (Local {OLLAMA_MODEL})...")
#         print("-" * 40)
#         print(ask_local_ollama(prompt))
#     else:
#         print("☁️  Thinking (Cloud API)...")
#         print("-" * 40)
#         print(ask_gemini(prompt))
#     print("-" * 40)

# if __name__ == "__main__":
#     main()

import sys
import subprocess
import os
import requests
import json
import time
import threading
import random
import itertools
import distro # pip install distro
from colorama import init, Fore, Style # pip install colorama

# Initialize Colorama for Windows compatibility
init(autoreset=True)

# --- CONFIGURATION ---
# "local" for Ollama, "api" for Gemini/OpenAI
MODE = "local"
# MODE = "api" 

# OLLAMA SETTINGS
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1" 

# GEMINI SETTINGS
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- ROAST TEMPLATES ---
ROASTS = {
    "success_carried": f"""
{Fore.GREEN}✅ STATUS: CARRIED
----------------------------------------
I literally mogged that syntax error. 
Your code was acting sus, but I locked in.
Here is the fix. You're welcome for the free elo.{Style.RESET_ALL}
""",
    "success_bare_minimum": f"""
{Fore.CYAN}✨ STATUS: BARE MINIMUM
----------------------------------------
Bro really tried to compile that? 💀
I fixed it, but barely. 
Next time, try using at least 1% of your brain.{Style.RESET_ALL}
""",
    "success_brainrot": f"""
{Fore.MAGENTA}🧠 STATUS: BIG BRAIN ENERGY
----------------------------------------
Your logic was cooked. 
I had to fanum tax that whole function.
It works now, no cap.{Style.RESET_ALL}
""",
    "failure": f"""
{Fore.RED}❌ STATUS: IT'S SO OVER
----------------------------------------
Nah. I can't even.
This isn't a bug, this is a crime scene.
I'm not fixing this.
Delete the repo and start a farm.{Style.RESET_ALL}
"""
}

# --- SPINNER LOGIC ---
def spinner_animation(event):
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    loading_texts = [
        "Scanning for brain cells...", 
        "Locating the skill issue...", 
        "Reading the docs (so you don't have to)...", 
        "Consulting the Elder Gods...", 
        "Mogging the compiler..."
    ]
    current_text = random.choice(loading_texts)
    
    while not event.is_set():
        sys.stdout.write(f'\r{Fore.YELLOW}{next(spinner)} {current_text} {Style.RESET_ALL}')
        sys.stdout.flush()
        time.sleep(0.1)
    
    # Clear the line when done
    sys.stdout.write('\r' + ' ' * (len(current_text) + 5) + '\r')

def get_system_context():
    """Returns OS and Shell info for better debugging"""
    try:
        if os.name == 'nt':
            os_name = "Windows " + os.environ.get('OS', '')
        else:
            os_name = distro.name(pretty=True)
        return f"{os_name} | Shell: {os.path.split(os.environ.get('SHELL', 'unknown'))[-1]}"
    except:
        return "Unknown OS"

def ask_local_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json().get('response', 'Error: No response from Ollama.')
    except Exception as e:
        return f"Error connecting to Ollama: {e}. Is 'ollama serve' running?"

def ask_gemini(prompt):
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY not set."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()

        if 'error' in response_data:
            return f"API Error: {response_data['error'].get('message', 'Unknown error')}"
        if 'promptFeedback' in response_data and response_data.get('candidates') is None:
            return "Error: The prompt was blocked by safety filters."
        if 'candidates' in response_data and response_data['candidates']:
            return response_data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error: Unexpected response format."

    except Exception as e:
        return f"Connection Error: {e}"

def main():
    if len(sys.argv) < 2:
        print(f"{Fore.RED}Usage: L <command_to_debug>{Style.RESET_ALL}")
        sys.exit(1)

    # 1. Get the last command that failed
    last_command = " ".join(sys.argv[1:])
    
    print(f"\n{Fore.BLUE}🔍 Analyzing: '{last_command}'...{Style.RESET_ALL}")

    # 2. Re-run it to capture stderr 
    try:
        process = subprocess.run(
            last_command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            timeout=10 
        )
        error_log = process.stderr + process.stdout
    except subprocess.TimeoutExpired:
        error_log = "Command timed out. It might be waiting for input."
    except Exception as e:
        error_log = str(e)

    if not error_log.strip():
        print(f"{Fore.GREEN}✅ Command ran successfully. No bugs found (miraculously).{Style.RESET_ALL}")
        sys.exit(0)

    # 3. Construct the prompt
    context = get_system_context()
    prompt = f"""
    You are a CLI terminal assistant named 'Brainless'. The user ran a command on {context} and it failed.
    
    COMMAND: {last_command}
    ERROR OUTPUT:
    {error_log[-2000:]} 
    
    Analyze the error. Provide a concise explanation and a specific SHELL COMMAND to fix it. 
    Do not use introductory text like "Here is the fix". Just give the explanation and the code.
    Be informal and brief.
    """

    # 4. Run AI with Spinner
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner,))
    
    spinner_thread.start()
    
    ai_response = ""
    try:
        if MODE == "local":
            ai_response = ask_local_ollama(prompt)
        else:
            ai_response = ask_gemini(prompt)
    finally:
        stop_spinner.set()
        spinner_thread.join()

    # 5. Output Result with Roast
    if "Error" in ai_response[:10]:
        print(ROASTS['failure'])
        print(f"{Fore.RED}{ai_response}{Style.RESET_ALL}")
    else:
        # Pick a random success roast
        roast_key = random.choice(["success_carried", "success_bare_minimum", "success_brainrot"])
        print(ROASTS[roast_key])
        print(ai_response)
        print("-" * 40)

if __name__ == "__main__":
    main()