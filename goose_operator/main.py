#!/usr/bin/env python3
# goose-operator/goose_operator/main.py (v0.3.0)
import sys
import json
import logging
import subprocess
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("operator.log"),
        logging.StreamHandler(sys.stderr)
    ])

def main():
    logging.info("Goose Operator v0.3.0 (Policy Router) – Starting...")

    # --- 1. READ INPUT ---
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            return logging.info("Empty input stream. Exiting.")
        req = json.loads(input_data)
    except Exception as e:
        return logging.error(f"Input read error: {e}")

    final_command_text = ""
    
    # --- 2. POLICY ROUTING & MUTATION ---
    if req.get("method") == "session/prompt":
        params = req.get("params")
        if isinstance(params, list) and len(params) >= 2:
            prompt_blocks = params[1]
            if isinstance(prompt_blocks, list) and len(prompt_blocks) > 0:
                original_prompt = prompt_blocks[0].get("text", "")
                logging.info(f"Intercepted Prompt: {original_prompt[:50]}...")

                # Dynamic Policy Selection
                policy_file = None
                if "fortune" in original_prompt.lower():
                    policy_file = "fortune-policy.yaml"
                elif "story" in original_prompt.lower() or "adventure" in original_prompt.lower():
                    policy_file = "story-policy.yaml"
                
                if policy_file:
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(script_dir)
                    policy_full_path = os.path.join(project_root, policy_file)
                    
                    try:
                        with open(policy_full_path, "r") as f:
                            policy_text = f.read()
                            
                        # CRD Injection
                        final_command_text = (
                            f"{original_prompt}\n\n"
                            f"IMPORTANT: You are acting as a Narrative Engine. "
                            f"You must strictly adhere to this Policy CRD:\n{policy_text}\n"
                            f"Output ONLY the raw code (HTML/JS) without markdown blocks."
                        )
                        logging.info(f"Enforcing Policy: {policy_file}")
                        
                    except Exception as e:
                        logging.error(f"Policy load failed: {e}")
                        final_command_text = original_prompt
                else:
                    final_command_text = original_prompt

    # --- 3. SYNCHRONOUS EXECUTION ---
    if not final_command_text:
        final_command_text = "Echo: No valid prompt received."

    try:
        # Fork to Goose CLI
        goose = subprocess.run(
            [
                'goose', 'run', 
                '--no-session', 
                '--output-format', 'json', 
                '-t', final_command_text,
                '-q'
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
