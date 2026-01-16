## 2. Get the Code
1.  **Clone the repository** into your WSL file system (e.g., `\\wsl.localhost\Ubuntu\home\user\`):
    ```bash
    git clone [https://github.com/tdk67/robot-test-wizard.git](https://github.com/tdk67/robot-test-wizard.git)
    ```

2.  **Navigate to the project folder:**
    *Note: The actual application code is in the subdirectory.*
    ```bash
    cd robot-test-wizard/ai-test-architect
    ```

3.  **Open in VS Code:**
    ```bash
    code .
    ```

---

## 3. Build the Environment
1.  When VS Code opens, you should see a notification (bottom-right): *"Folder contains a Dev Container configuration file."*
2.  Click **Reopen in Container**.
    * *Alternative:* Press `F1` -> Select **Dev Containers: Reopen in Container**.
3.  **Wait:** Docker will build the image and install all Python dependencies automatically.

---

## 4. Configuration
Secrets are not stored in GitHub for security. You must create them locally.

1.  **Create `.env` file:**
    Create a new file named `.env` in the root of the `ai-test-architect` folder:
    ```ini
    OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
    ```

2.  **Streamlit Config (Optional):**
    If you want to suppress the "Email" prompt, ensure `.streamlit/config.toml` exists:
    ```toml
    [server]
    headless = true
    address = "0.0.0.0"
    port = 8501
    [browser]
    gatherUsageStats = false
    ```

3.  **Verify Permissions:**
    Ensure the start script is executable:
    ```bash
    chmod +x start.sh
    ```

---

## 5. Launch
Run the full system (Backend + Frontend):
```bash
./start.sh
```
* **Frontend:** [http://localhost:8501](http://localhost:8501)
* **Backend:** [http://localhost:8000/docs](http://localhost:8000/docs)