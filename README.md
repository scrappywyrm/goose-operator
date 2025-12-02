# Goose Operator (Stage 1)

**An ACP-native Admission Controller for Self-Healing Agentic AI.**

This project implements the Kubernetes Operator pattern for the [Goose](https://github.com/block/goose) Agent. It acts as a transparent sidecar proxy between the editor (Zed/VS Code) and the Goose binary, intercepting prompts to enforce declarative policies via **ReconcilerGoal CRDs**.

### Features (v0.1)
* **Two-Legged Proxy:** Spawns `goose acp` as a subprocess and acts as a middleware layer.
* **Admission Control:** Intercepts `session/prompt` to enforce policies (e.g., blocking risky actions) before the agent receives the request.
* **ACP Native:** Works seamlessly with any ACP-compatible client (Zed, etc.) without requiring editor plugins.

### Future Roadmap
* **Advanced Policy Logic:** Moving beyond regex to semantic, context-aware policy enforcement.
* **Smart Arbitration:** Using lightweight models to evaluate prompt safety and alignment in real-time.
* **Self-Healing Loops:** Automated detection and recovery strategies for agent failures and hallucinations.

### Installation

1. **Prerequisites:**
   * Rust (for building Goose CLI) or existing `goose` installation.
   * Python 3.10+

2. **Setup:**
   ```bash
   # Clone the repo
   git clone [https://github.com/YOURUSERNAME/goose-operator.git](https://github.com/YOURUSERNAME/goose-operator.git)
   cd goose-operator

   # Setup virtual environment
   python3 -m venv venv
   source venv/bin/activate
