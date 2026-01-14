# AI Test Architect (MVP)

An intelligent agent that runs inside a Docker container to generate, execute, and analyze Robot Framework tests.

## Architecture
* **Environment:** Pure WSL 2 + Native Docker Engine (Ubuntu 24.04).
* **Core:** Python 3.12 + LangChain + Streamlit.
* **Testing:** Robot Framework 7.0.
* **Storage:** Tests are generated in `./tests` and results in `./results`.

## Project Structure
```text
/workspaces/ai-test-architect (Root)
├── .devcontainer/     # VS Code Docker config
├── .streamlit/        # Streamlit headless config
├── tests/             # Generated Robot files (Persistent)
├── results/           # Execution logs/reports (Persistent)
├── app.py             # The AI Agent
├── Dockerfile         # Environment definition
└── project.md         # Auto-generated index of available tests
```

## Usage

### 1. Standard Launch
If port 8501 is free, simply run:
```bash
streamlit run app.py
```
* **Access:** Open `http://localhost:8501` in your Windows browser.

### 2. Custom Port (If 8501 is busy)
If you have other instances running or encounter port conflicts, run on a specific port (e.g., 8502):

```bash
streamlit run app.py --server.port 8502
```
* **Access:** Open `http://localhost:8502` in your Windows browser.

### 3. Workflow
1.  **Chat:** Ask the agent to "Write a hello world test named login.robot".
2.  **Verify:** Check the **Explorer Sidebar** to see the file appear.
3.  **Run:** Ask the agent to "Run login.robot".
4.  **Monitor:** Watch the **Runner Status** in the sidebar. It runs in the background so the UI remains responsive.

## Troubleshooting
* **Files not appearing?** Ensure you are running `app.py` from the project root and that your `devcontainer.json` does NOT have a manual `workspaceMount` override.
* **App hangs on start?** Ensure `.streamlit/config.toml` exists with `headless = true`.