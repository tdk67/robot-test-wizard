# PLAN.md

## 1. Project Status
* **Phase:** Phase 0 - Environment & Hello World.
* **Goal:** A "Hello World" Robot Framework test executed by an AI Agent inside a Pure WSL Docker container.

## 2. Architecture (Pure WSL)
* **Host:** Windows 10/11 (UI).
* **Execution:** WSL 2 (Ubuntu 22.04).
* **Container:** Native Docker Engine (Linux).
* **Agent:** Streamlit + LangChain (Minimal "Hello World" capability).
* **Test:** Pure Robot Framework `Log` command.

## 3. Implementation Steps
1.  [x] **INSTALL.md:** Detailed WSL guide + Native Docker + **Vi Instructions**.
2.  [ ] **Dockerfile:** Python 3.12 + Robot Framework.
3.  [ ] **Agent (app.py):** Reader/Writer/Executor capabilities.
4.  [ ] **Hello World:** Verify "Log Hello" works.