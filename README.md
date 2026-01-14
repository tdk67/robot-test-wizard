# AI Test Architect (MVP)

A minimal implementation of an AI-driven Test Agent running in Docker.

## Structure
* `app.py`: The AI Agent (Streamlit UI).
* `tests/`: Directory where the Agent writes tests.
* `results/`: Directory where Robot outputs logs.

## Quick Start
1.  **Setup:** Follow `INSTALL.md` to set up WSL and Docker.
2.  **Open:** Open this folder in VS Code, press `F1`, select **"Dev Containers: Reopen in Container"**.
3.  **Run:** `streamlit run app.py`