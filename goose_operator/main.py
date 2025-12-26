#!/usr/bin/env python3
# goose-operator/goose_operator/main.py (v0.9.0 - The Chaos Monkey)
import sys, json, logging, subprocess, os

script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, "..", "operator.log")
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', 
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stderr)])

def main():
    logging.info("Goose Operator v0.9.0 (The Chaos Monkey) – Starting...")
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
    p_lower = original_prompt.lower()
    policy_file = None

    # --- ROUTING LOGIC ---
    if "triage" in p_lower or "issue" in p_lower or "github" in p_lower: policy_file = "triage-policy.yaml"
    elif "resume" in p_lower or "career" in p_lower: policy_file = "career-policy.yaml"
    elif "detective" in p_lower or "lost" in p_lower: policy_file = "detective-policy.yaml"
    elif "clean" in p_lower or "json" in p_lower or "napkin" in p_lower: policy_file = "data-policy.yaml"
    elif "query" in p_lower or "sql" in p_lower or "database" in p_lower: policy_file = "sql-policy.yaml"
    elif "api" in p_lower or "swagger" in p_lower or "spec" in p_lower or "openapi" in p_lower: policy_file = "api-policy.yaml"
    
    # NEW: Day 12 Chaos Routing
    elif "chaos" in p_lower or "load" in p_lower or "test" in p_lower or "simulation" in p_lower: policy_file = "chaos-policy.yaml"

    # Legacy policies
    elif "fortune" in p_lower: policy_file = "fortune-policy.yaml"
    elif "story" in p_lower: policy_file = "story-policy.yaml"
    elif "cocoa" in p_lower: policy_file = "cocoa-policy.yaml"
    elif "deploy" in p_lower: policy_file = "deployment-policy.yaml"
    elif "hud" in p_lower: policy_file = "interface-policy.yaml"

    # --- EXECUTION ---
    final_command_text = original_prompt
    if policy_file:
        try:
            with open(os.path.join(os.path.dirname(script_dir), policy_file), "r") as f:
                final_command_text = f"{original_prompt}\n\nIMPORTANT: Adhere to this CRD:\n{f.read()}"
            logging.info(f"Enforcing Policy: {policy_file}")
        except: pass

    try:
        goose = subprocess.run(['goose', 'run', '-t', final_command_text, '-q'], 
                               capture_output=True, text=True, check=True)
        print(goose.stdout)
    except subprocess.CalledProcessError as e: print(f"Error: {e.stderr}")

if __name__ == "__main__": main()
