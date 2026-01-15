# 🧙‍♂️ Setup Guide: Installation Wizard

This guide will help you prepare your Windows machine to run the **AI Test Architect Installation Wizard**. The wizard will then guide you through the complex parts (WSL, Docker, etc.).

---

## Step 1: Install Python 3.12
The wizard is optimized for Python 3.12.

1.  **Download:** Go to [Python 3.12.10 Downloads](https://www.python.org/downloads/release/python-3120/) (or the latest 3.12.x release).
2.  **Run Installer:** Scroll to "Files" and download the **Windows installer (64-bit)**.
3.  **Critical Step:** When running the installer, verify you check the box:
    * `[ ] Add Python to PATH` (If this is your only Python version)
    * *If you have other versions, see Step 2.*

---

## Step 2: Verify & Manage Versions
Open **PowerShell** and check which Python is active.

```powershell
python --version
```

### 🔴 Scenario A: It says "Python 3.12.x"
Great! You are ready. Skip to **Step 3**.

### 🟡 Scenario B: It says "Python 3.10" (or older)
If you have multiple versions installed, you need to ensure we use 3.12 for this project.

**Option 1: The "py" Launcher (Easiest)**
Windows comes with a launcher that lets you pick versions easily. Try this:
```powershell
py -3.12 --version
```
*If this works, use `py -3.12` instead of `python` in all future commands.*

**Option 2: Force Environment Variable (Temporary)**
You can force the current PowerShell terminal to use Python 3.12 by setting it at the front of your PATH for this session only.

1.  Find where you installed Python 3.12 (usually `C:\Users\<YOU>\AppData\Local\Programs\Python\Python312`).
2.  Run this command (replace `<YOU>` with your actual username):
    ```powershell
    $env:Path = "C:\Users\<YOU>\AppData\Local\Programs\Python\Python312;" + $env:Path
    ```
3.  Verify again:
    ```powershell
    python --version
    # Should now show 3.12.10
    ```

---

## Step 3: Create a Virtual Environment
Isolate the wizard dependencies so they don't mess up your system.

1.  Navigate to the folder where you saved `install_wizard.py`.
    ```powershell
    cd path\to\your\folder
    ```
2.  Create the environment (named `venv`):
    *Standard:*
    ```powershell
    python -m venv venv
    ```
    *If using Option 1 above:*
    ```powershell
    py -3.12 -m venv venv
    ```

---

## Step 4: Activate the Environment
You must activate the environment every time you open a new terminal to work on this project.

```powershell
.\venv\Scripts\Activate
```

* **Success:** You should see `(venv)` appear at the start of your command prompt line.
* **Error?** If you see "script is not signed...", run this command to allow local scripts:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    ```
    Then try activating again.

---

## Step 5: Install Requirements
Install the libraries required to run the Wizard itself.

1.  Create a file named `wizard_requirements.txt` with these contents:
    ```text
    streamlit
    requests
    python-dotenv
    langchain
    langchain-openai
    ```
2.  Install them:
    ```powershell
    pip install -r wizard_requirements.txt
    ```

---

## Step 6: Launch the Wizard 🧙‍♂️
Everything is ready. Start the application:

```powershell
streamlit run install_wizard.py
```

* A browser window will open automatically at `http://localhost:8501`.
* Follow the on-screen instructions to set up your full AI Test Architect environment.