#!/usr/bin/env python3
# goose-operator/goose_operator/main.py (v0.6.0 - Triage & Pipe Support)
import sys
import json
import logging
import subprocess
import os

# Configure Logging
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, "..", "operator.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)
    ])

def main():
    logging.info("Goose Operator v0.6.0 (Refactor) – Starting...")

    # --- 1. READ INPUT (Hybrid: JSON or Raw Text) ---
    original_prompt = ""
    try:
        if not sys.stdin.isatty():
            input_data = sys.stdin.read()
            if not input_data.strip():
                return logging.info("Empty input stream. Exiting.")
            
            # Attempt 1: Parse as JSON (Extension Mode)
            try:
                req = json.loads(input_data)
                if req.get("method") == "session/prompt":
                    params = req.get("params")
                    if isinstance(params, list) and len(params) >= 2:
                        prompt_blocks = params[1]
                        if isinstance(prompt_blocks, list) and len(prompt_blocks) > 0:
                            original_prompt = prompt_blocks[0].get("text", "")
            except json.JSONDecodeError:
                # Attempt 2: Fallback to Raw Text (Pipe Mode)
                logging.info("Input is not JSON. Treating as raw text pipe.")
                original_prompt = input_data

    except Exception as e:
        return logging.error(f"Input read error: {e}")

    if not original_prompt:
        original_prompt = "Status Check"
        
    logging.info(f"Intercepted Prompt: {original_prompt[:50]}...")

    # --- 2. POLICY ROUTING ---
    policy_file = None
    p_lower = original_prompt.lower()

    # Domain: Fun & Story
    if "fortune" in p_lower:
        policy_file = "fortune-policy.yaml"
    elif "story" in p_lower or "adventure" in p_lower:
        policy_file = "story-policy.yaml"
    elif "cocoa" in p_lower or "chart" in p_lower:
        policy_file = "cocoa-policy.yaml"
    
    # Domain: Ops & Deployment
    elif "deploy" in p_lower:
        policy_file = "deployment-policy.yaml"
    elif "hud" in p_lower or "gesture" in p_lower:
        policy_file = "interface-policy.yaml"

    # Domain: Triage (Day 6f)
    elif "triage" in p_lower or "issue" in p_lower or "github" in p_lower:
        policy_file = "triage-policy.yaml"
        
    # Domain: Data & Career (Day 8f, 9f)
    elif "clean" in p_lower or "json" in p_lower or "napkin" in p_lower or "detective" in p_lower:
        policy_file = "data-policy.yaml"
    elif "resume" in p_lower or "cv" in p_lower or "career" in p_lower:
        policy_file = "career-policy.yaml"

    # --- 3. POLICY INJECTION ---
    final_command_text = original_prompt
    
    if policy_file:
        # Robust Path Logic
        project_root = os.path.dirname(script_dir)
        policy_full_path = os.path.join(project_root, policy_file)
        
        try:
            with open(policy_full_path, "r") as f:
                policy_text = f.read()
                
                # CRD Injection
                final_command_text = (
                    f"{original_prompt}\n\n"
                    f"IMPORTANT: You are acting as a Specialized Engine. "
                    f"You must strictly adhere to this Policy CRD:\n{policy_text}\n"
                )
                logging.info(f"Enforcing Policy: {policy_file}")
                
        except FileNotFoundError:
            logging.error(f"CRITICAL: Policy file not found at {policy_full_path}")
        except Exception as e:
            logging.error(f"Policy load failed: {e}")

    # --- 4. EXECUTION ---
    try:
        # We use standard text output for piping compatibility
        goose = subprocess.run(
            [
                'goose', 'run', 
                '-t', final_command_text,
                '-q' # Quiet mode
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=300
        )
        
        # Output Forwarding
        sys.stdout.write(goose.stdout)
        sys.stdout.flush()
        logging.info("CLI run complete.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Goose failed: {e.stderr}")
        sys.stdout.write(f"❌ ERROR: {e.stderr}")
    except Exception as e:
        logging.error(f"Critical: {e}")

if __name__ == "__main__":
    main()
