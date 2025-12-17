# README still under construction 

# Goose Operator (Stage 1)

**An ACP-native Admission Controller for Self-Healing Agentic AI.**

This project implements the Kubernetes Operator pattern for the [Goose](https://github.com/block/goose) Agent. It acts as a transparent sidecar proxy that intercepts editor commands (ACP JSON) and enforces declarative policies via **ReconcilerGoal CRDs**.

---

### Architectural Pivot (The v0.2.1 Status) 🛠️

Due to instability that i've run into in the experimental `goose acp` binary, the Operator's execution layer has been pivoted to the stable, proven `goose run` CLI interface.

| Feature | Description | Architecture |
| :--- | :--- | :--- |
| **Two-Legged Proxy** | The Operator sits between the Client (Editor) and the Goose binary. | Spawns `goose run --output-format json` as a subprocess. |
| **Admission Control** | Intercepts ACP's `session/prompt` (inbound) and translates/mutates the JSON into a stable CLI command (outbound). | Policy check occurs *before* execution; the prompt is injected into the command. |
| **ACP Compliant Input** | The Operator correctly receives and deserializes the full ACP request lifecycle (Initialize, Session/New, Prompt). | Ensures the solution remains viable for official ACP use when the upstream binary is fixed. |

---

### Future Roadmap

* **Advanced Policy Logic:** Moving beyond regex to semantic, context-aware policy enforcement.
* **Smart Arbitration:** Using lightweight models to evaluate prompt safety and alignment in real-time.
* **Self-Healing Loops:** Automated detection and recovery strategies for agent failures and hallucinations.

---

### Installation

1. **Prerequisites:**
   * Rust (for building Goose CLI) or existing `goose` installation (v1.15.0+).
   * Python 3.10+

2. **Setup:**
   ```bash
   # Clone the repo
   git clone [https://github.com/YOURUSERNAME/goose-operator.git](https://github.com/YOURUSERNAME/goose-operator.git)
   cd goose-operator

   # Setup virtual environment
   python3 -m venv venv
   source venv/bin/activate
