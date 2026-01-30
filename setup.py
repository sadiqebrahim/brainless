import os
import sys
import platform
import subprocess

# --- CONFIGURATION ---
TARGET_SCRIPT = "brainless.py"  # The script we are running
COMMAND_NAME = "imdumb"     # The full command
SHORT_ALIAS = "L"               # The shortcut
REQUIRED_LIBS = ["requests", "distro", "colorama"]

def print_step(msg):
    print(f"\n🔵 [STEP] {msg}...")

def print_success(msg):
    print(f"✅ [SUCCESS] {msg}")

def print_error(msg):
    print(f"❌ [ERROR] {msg}")

def install_dependencies():
    """Installs required Python libraries automatically."""
    print_step("Installing dependencies (colorama, distro, requests)")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + REQUIRED_LIBS)
        print_success("Dependencies installed.")
    except subprocess.CalledProcessError:
        print_error("Failed to install dependencies. Check your pip setup.")
        sys.exit(1)

def get_abs_script_path():
    """Gets the absolute path of brainless.py in the current folder."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, TARGET_SCRIPT)
    
    if not os.path.exists(script_path):
        print_error(f"Could not find '{TARGET_SCRIPT}' in {current_dir}.")
        print("   Make sure install.py and brainless.py are in the same folder!")
        sys.exit(1)
    
    return script_path

def setup_unix(script_path):
    """Handles Linux (Bash) and macOS (Zsh/Bash)."""
    shell = os.environ.get("SHELL", "")
    home = os.path.expanduser("~")
    
    # Detect Config File
    config_file = os.path.join(home, ".bashrc") # Default to Linux
    if "zsh" in shell:
        config_file = os.path.join(home, ".zshrc")
    elif platform.system() == "Darwin": # Mac default fallback
        config_file = os.path.join(home, ".bash_profile")

    print_step(f"Configuring shell: {config_file}")
    
    # Define the alias lines
    # 1. The main command 'skillissue' points to the python script
    # 2. The shortcut 'L' points to 'skillissue'
    alias_block = f"""
# --- BRAINLESS AI DEBUGGER ---
alias {COMMAND_NAME}='python3 {script_path} "$(tail -n 4 "$(ls -t ~/.terminal_logs/*.log 2>/dev/null | head -n 1)")"'
alias {SHORT_ALIAS}="{COMMAND_NAME}"
# -----------------------------


# Auto-log terminal session
LOGDIR="$HOME/.terminal_logs"
mkdir -p "$LOGDIR"

# Only start once, only in interactive shells
if [[ $- == *i* ]] && [[ -z "$TERMINAL_LOGGING" ]]; then
  export TERMINAL_LOGGING=1
  script -q -f "$LOGDIR/$(date '+%Y-%m-%d_%H-%M-%S')_pid$$.log"
  exit
fi
"""
    
    # Read existing
    try:
        with open(config_file, "r") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""

    # Append if not exists
    if f'alias {COMMAND_NAME}=' in content:
        print_success(f"Aliases already exist in {config_file}. Skipping.")
    else:
        with open(config_file, "a") as f:
            f.write(alias_block)
        print_success(f"Aliases added to {config_file}")

    return config_file

def setup_windows(script_path):
    """Handles Windows PowerShell."""
    print_step("Configuring PowerShell Profile")

    # Get Profile Path via PowerShell command
    try:
        profile_path = subprocess.check_output(
            ["powershell", "-Command", "echo $PROFILE"], 
            text=True
        ).strip()
    except:
        print_error("Could not find PowerShell profile.")
        return None

    # Ensure directory exists
    profile_dir = os.path.dirname(profile_path)
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir, exist_ok=True)

    logging_block = r"""
# --- AUTO-LOG TERMINAL SESSION (PowerShell) ---
$LogDir = "$HOME\.terminal_logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# Only start once per session
if (-not $env:TERMINAL_LOGGING) {
    $env:TERMINAL_LOGGING = "1"

    $ts = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $pid = $PID
    $LogFile = Join-Path $LogDir "${ts}_pid${pid}.log"

    Start-Transcript -Path $LogFile -Append | Out-Null
}
# --------------------------------------------
"""
    # Define the functions for PowerShell
    function_block = f"""
# --- BRAINLESS AI DEBUGGER ---
function {COMMAND_NAME} {{
    python "{script_path}" @args
}}
function {SHORT_ALIAS} {{
    {COMMAND_NAME} @args
}}
# -----------------------------

"""
    existing = ""
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            existing = f.read()

    # Prevent duplicates
    already_has_logging = "AUTO-LOG TERMINAL SESSION (PowerShell)" in existing
    already_has_brainless = f"function {COMMAND_NAME}" in existing

    # Append only missing blocks
    with open(profile_path, "a", encoding="utf-8") as f:
        if not already_has_logging:
            f.write("\n" + logging_block + "\n")
            print_success("PowerShell auto-logging added to Profile.")
        else:
            print_success("PowerShell auto-logging already exists. Skipping.")

        if not already_has_brainless:
            f.write("\n" + function_block + "\n")
            print_success("Brainless functions added to Profile.")
        else:
            print_success("Brainless functions already exist in Profile. Skipping.")

    print_success(f"Profile updated: {profile_path}")
    return profile_path


def main():
    print("🧠 \033[1mBRAINLESS INSTALLER\033[0m")
    print("---------------------------------")
    
    # 1. Install Libs
    install_dependencies()

    # 2. Get Script Path
    script_path = get_abs_script_path()
    
    # 3. Setup Shell
    config_file = None
    if os.name == 'nt':
        config_file = setup_windows(script_path)
        cmd_instruction = "Restart your PowerShell"
    else:
        config_file = setup_unix(script_path)
        cmd_instruction = f"source {config_file}"

    print("\n" + "="*40)
    print(f"✨ \033[92mINSTALLATION COMPLETE\033[0m ✨")
    print("="*40)
    print("To finish setup, run this command right now:")
    print(f"\n    \033[1m{cmd_instruction}\033[0m\n")
    # print(f"Then use either command:")
    # print(f"    1. \033[1m{COMMAND_NAME}\033[0m <command>")
    # print(f"    2. \033[1m{SHORT_ALIAS}\033[0m <command>")

if __name__ == "__main__":
    main()


