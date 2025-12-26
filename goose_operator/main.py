#!/usr/bin/env python3
# goose-operator/goose_operator/main.py (v0.18.1 - Campaign Edition)
import sys, json, logging, subprocess, os

script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, "..", "operator.log")
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', 
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stderr)])

def get_environmental_context():
    """Scans the current directory for relevant files."""
    context_data = ""
    if os.path.exists("staff_notes.txt"):
        with open("staff_notes.txt", "r") as f:
            context_data += f"\n\n[CONTEXT FILE: staff_notes.txt]\n{f.read()}\n"
    return context_data

def main():
    logging.info("Goose Operator v0.18.1 (Campaign Edition) – Starting...")
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
    # 1. Day 15: Social Campaign (NEW)
    if "social" in p_lower or "campaign" in p_lower or "instagram" in p_lower or "twitter" in p_lower or "facebook" in p_lower: policy_file = "campaign-policy.yaml"

    # 2. Day 14: Skills
    elif "skill" in p_lower or "manual" in p_lower or "ops" in p_lower: policy_file = "skills-policy.yaml"

    # 3. Day 13: Scheduler
    elif "schedule" in p_lower or "staff" in p_lower or "roster" in p_lower: policy_file = "scheduling-policy.yaml"

    # 4. Day 12: Council
    elif "council" in p_lower or "debate" in p_lower or "mascot" in p_lower: policy_file = "council-policy.yaml"

    # 5. Day 11: Photo Booth
    elif "photo" in p_lower or "booth" in p_lower: policy_file = "photobooth-policy.yaml"

    # 6. Day 10: Posters
    elif "poster" in p_lower: policy_file = "poster-policy.yaml"

    # 7. Day 9: Tags
    elif "tag" in p_lower or "gift" in p_lower: policy_file = "gift-policy.yaml"

    # 8. Day 8: Vendor
    elif "vendor" in p_lower or "dmitri" in p_lower: policy_file = "vendor-policy.yaml"

    # 9. Day 7: Detective
    elif "detective" in p_lower or "lost" in p_lower: policy_file = "detective-policy.yaml"

    # Legacy
    elif "review" in p_lower: policy_file = "review-policy.yaml"
    elif "fix" in p_lower: policy_file = "fixer-policy.yaml"
    elif "chaos" in p_lower: policy_file = "chaos-policy.yaml"
    elif "query" in p_lower or "sql" in p_lower: policy_file = "sql-policy.yaml"
    
    # Fallbacks
    elif "triage" in p_lower: policy_file = "triage-policy.yaml"
    elif "clean" in p_lower or "json" in p_lower: policy_file = "data-policy.yaml"

    # --- EXECUTION ---
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
