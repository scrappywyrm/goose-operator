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
                
                # quick policy check: block friday deploys
                if "deploy" in prompt.lower() and "friday" in prompt.lower():
                    logging.warning("Blocking request due to SafetyGoal CRD")
                    send({
                        "jsonrpc": "2.0",
                        "method": "session/update",
                        "params": {
                            "sessionId": req["params"]["sessionId"],
                            "updates": [{
                                "type": "text",
                                "text": "🛑 **BLOCKED by Goose Operator**: No deployments on Fridays."
                            }]
                        }
                    })
                    continue  # BLOCK: drop the packet, don't forward to goose
            # --------------------------------

            # forward valid requests to real goose
            goose.stdin.write(line)
            goose.stdin.flush()

        except Exception as e:
            logging.error(f"Error processing input: {e}")

    goose.terminate()

if __name__ == "__main__":
    main()
