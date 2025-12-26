#!/usr/bin/env python3
# goose-operator/goose_operator/main.py (v0.20.0 - Wishlist Edition)
import sys, json, logging, subprocess, os

script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, "..", "operator.log")
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', 
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stderr)])

def get_environmental_context():
    """Scans for local files to inject context."""
    context_data = ""
    # Day 17: Wishlist Database (Inject current state)
    if os.path.exists("wishes.json"):
        with open("wishes.json", "r") as f:
            context_data += f"\n\n[CURRENT WISHBOX STATE (wishes.json)]\n{f.read()}\n"
    
    # Legacy Contexts
    if os.path.exists(".goosehints"):
        with open(".goosehints", "r") as f: context_data += f"\n\n[PROJECT RULES]\n{f.read()}\n"
    if os.path.exists("INSTRUCTIONS.md"):
        with open("INSTRUCTIONS.md", "r") as f: context_data += f"\n\n[PLAN]\n{f.read()}\n"

    return context_data

def main():
    logging.info("Goose Operator v0.20.0 (Wishlist Edition) – Starting...")
    original_prompt = ""
    try:
        if not sys.stdin.isatty():
            input_data = sys.stdin.read()
            try:
                req = json.loads(input_data)
                if req.get("method") == "session/prompt":
                    params = req.get("params", [])
                    if len(params) >= 2: original_prompt = params[1][0].get("text", "")
            except: original_prompt = input_data
    except Exception as e: return logging.error(f"Input read error: {e}")

    if not original_prompt: original_prompt = "Status Check"
    full_prompt = original_prompt + get_environmental_context()
    p_lower = original_prompt.lower()
    policy_file = None

    # --- ROUTING LOGIC ---
    if "wish" in p_lower or "fairy" in p_lower or "grant" in p_lower: policy_file = "wishlist-policy.yaml"
    elif "countdown" in p_lower or "app" in p_lower or "hint" in p_lower: policy_file = "countdown-policy.yaml"
    elif "social" in p_lower or "campaign" in p_lower: policy_file = "campaign-policy.yaml"
    elif "skill" in p_lower or "ops" in p_lower: policy_file = "skills-policy.yaml"
    elif "schedule" in p_lower or "staff" in p_lower: policy_file = "scheduling-policy.yaml"
    elif "council" in p_lower or "mascot" in p_lower: policy_file = "council-policy.yaml"
    elif "photo" in p_lower or "booth" in p_lower: policy_file = "photobooth-policy.yaml"
    elif "poster" in p_lower: policy_file = "poster-policy.yaml"

    final_command_text = full_prompt
    if policy_file:
        try:
            with open(os.path.join(os.path.dirname(script_dir), policy_file), "r") as f:
                final_command_text = f"{full_prompt}\n\nIMPORTANT: Adhere to this CRD:\n{f.read()}"
            logging.info(f"Enforcing Policy: {policy_file}")
        except: pass

    try:
        goose = subprocess.run(['goose', 'run', '-t', final_command_text, '-q'], 
                               capture_output=True, text=True, check=True)
        print(goose.stdout)
    except subprocess.CalledProcessError as e: print(f"Error: {e.stderr}")

if __name__ == "__main__": main()
