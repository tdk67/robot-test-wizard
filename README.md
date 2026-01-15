# AI Test Architect 🐧

An intelligent QA Agent that generates and runs Robot Framework tests using a decoupled **Client-Server Architecture**.

* **Frontend:** Streamlit (Port 8501)
* **Backend:** FastAPI (Port 8000)
* **Agent:** LangChain + OpenAI GPT-4o
* **Execution:** Robot Framework 7.0 (Native Linux)

## 🚀 Quick Start

### 1. Start the Application
Run the supervisor script to launch the Backend and Frontend simultaneously:
```bash
./start.sh
```

### 2. Usage
1.  **Open Browser:** Go to [http://localhost:8501](http://localhost:8501).
2.  **Generate Test:** Type in the chat: *"Write a login test for example.com"*.
3.  **Run Test:** Click the **▶️ Play Button** in the sidebar.
    * The logs will stream in real-time.
    * A generic HTML report will be generated in `./results/`.

## 📂 Architecture
```text
/workspaces/ai-test-architect
├── backend/             # FastAPI Server & AI Logic
├── frontend/            # Streamlit UI Client
├── tests/               # Generated Robot Framework files
├── results/             # Execution reports (log.html, report.html)
└── .devcontainer/       # Docker environment config
```

## 🛠 Troubleshooting
* **"Workspace does not exist":** If VS Code complains, ensure you cloned the repo into the WSL file system, not `/mnt/c/`.
* **"API Key Missing":** Ensure you created the `.env` file (see `INSTALL.md`).
* **"Connection Refused":** Make sure `./start.sh` is running and the Backend port (8000) is not blocked.