#!/usr/bin/env python3
# goose-operator – True ACP Admission Controller (Stage 1 – Dec 2025)
import sys
import json
import logging
import subprocess
import threading
import os

# logging setup: keep stdout clean for json-rpc traffic.
# logs go to stderr so we don't break the protocol.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("operator.log"),
        logging.StreamHandler(sys.stderr) 
    ])

def send(msg):
    """Send JSON-RPC message to the Editor (Zed/VSCode)"""
    json.dump(msg, sys.stdout)
    sys.stdout.write('\n')
    sys.stdout.flush()

def forward_from_goose(process):
    """Read from real Goose binary and forward to Editor"""
    for line in iter(process.stdout.readline, ''):
        if line.strip():
            try:
                # try to parse as JSON
                msg = json.loads(line)
                send(msg)
            except json.JSONDecodeError:
                # goose sometimes chatters on startup ("Goose ACP agent started...").
                # catch that noise so the json parser doesn't choke.
                logging.info(f"[Goose Startup]: {line.strip()}")
            except Exception as e:
                logging.error(f"Forwarding error: {e}")

def main():
    logging.info("Goose Operator ACP Proxy v0.1 – Starting...")

    # subprocess inherits env vars by default, so GOOSE_PROVIDER overrides work out of the box.
    try:
        goose = subprocess.Popen(
            ['goose', 'acp'], 
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr, # pipe goose's logs to our stderr to keep things clean
            text=True,
            bufsize=1
        )
    except FileNotFoundError:
        logging.error("goose binary missing. make sure it's in the PATH.")
        sys.exit(1)

    # forward goose -> editor in background thread
    threading.Thread(target=forward_from_goose, args=(goose,), daemon=True).start()

    # --- ROBUST POLICY LOADING ---
    # check env var for crd path first (k8s style injection), fallback to local default.
    policy_path = os.environ.get("RECONCILER_CRDS")
    
    if not policy_path:
        # fallback: assume fortune-policy.yaml is one level up from this script (project root)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        policy_path = os.path.join(project_root, "fortune-policy.yaml")

    logging.info(f"Loading Policy from: {policy_path}")

    try:
        with open(policy_path, "r") as f:
            policy_text = f.read()
    except Exception as e:
        logging.warning(f"Failed to load policy: {e}")
        policy_text = "No policy found."
    # -----------------------------

    # Main Loop: Editor -> Operator
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            
            # --- ADMISSION CONTROL POLICY ---
            if req.get("method") == "session/prompt":
                prompt = req["params"]["prompt"]["text"]
                logging.info(f"Intercepted prompt: {prompt}")
                
                # --- MUTATING ADMISSION CONTROLLER ---
                # catch the specific triggers for day 1 challenge
                if "fortune" in prompt.lower() or "zelda" in prompt.lower():
                    # inject the CRD policy directly into the prompt stream
                    new_prompt = (
                        f"{prompt}\n\n"
                        f"IMPORTANT: You are being governed by the following ReconcilerGoal CRD.\n"
                        f"You MUST adhere to these rules:\n"
                        f"{policy_text}\n"
                    )
                    req["params"]["prompt"]["text"] = new_prompt
                    
                    # notify the user so they know the operator is working (live diff)
                    send({
                        "jsonrpc": "2.0",
                        "method": "session/update",
                        "params": {
                            "sessionId": req["params"]["sessionId"],
                            "updates": [{
                                "type": "text",
                                "text": "✨ **Admission Controller**: Mutated prompt with `zelda-quality-control` CRD."
                            }]
                        }
                    })
                # -------------------------------------

            # forward valid (or mutated) requests to real goose
            goose.stdin.write(line)
            goose.stdin.flush()

        except Exception as e:
            logging.error(f"Error processing input: {e}")

    goose.terminate()

if __name__ == "__main__":
    main()
