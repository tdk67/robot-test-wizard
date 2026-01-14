# Installation Guide: AI Test Architect (Pure WSL Method)

This guide sets up a professional Linux development environment on Windows. It uses the native Linux Docker engine for maximum performance and avoids "Docker Desktop" licensing/performance issues.

---

## Step 1: WSL 2 Setup (The Foundation)
Even if you have WSL, follow these steps to ensure you have a clean, isolated environment.

### 1.1 Install/Update WSL
1.  Open **PowerShell** as Administrator.
2.  Run: `wsl --update`
3.  Run: `wsl --list --online` to see available distributions.

### 1.2 Install a Fresh Distro (Recommended)
1.  Run: `wsl --install -d Ubuntu-24.04` (or your preferred version).
2.  Wait for the console to open.
3.  Create a **username** and **password** when prompted.
    * *Note:* Linux passwords do not show characters while typing.

### 1.3 Verify Version
In PowerShell, run: `wsl -l -v`
* Ensure your distribution is set to version **2**.
* If not, run: `wsl --set-version Ubuntu-24.04 2`

---

## Step 2: Enable Systemd (Crucial for Docker)
Native Docker requires `systemd` to run as a service.

1.  Inside your **Ubuntu terminal**: `sudo vi /etc/wsl.conf`
2.  Press `i` to enter Insert Mode.
3.  Add these lines:
    ```ini
    [boot]
    systemd=true
    ```
4.  Press `Esc`, then type `:wq` and `Enter` to save.
5.  **Restart WSL:**
    * Close the Ubuntu terminal.
    * In PowerShell: `wsl --shutdown`
    * Open Ubuntu again.

---

## Step 3: Install Docker Engine (Native Linux)
Run these commands inside your **Ubuntu terminal** block by block.

1.  **Clean up old versions:**
    ```bash
    for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
    ```

2.  **Set up Repository (Copy block):**
    ```bash
    sudo apt-get update
    sudo apt-get install ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL [https://download.docker.com/linux/ubuntu/gpg](https://download.docker.com/linux/ubuntu/gpg) | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] [https://download.docker.com/linux/ubuntu](https://download.docker.com/linux/ubuntu) \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```

3.  **Install Engine:**
    ```bash
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

4.  **Fix Permissions (The "Permission Denied" Fix):**
    ```bash
    sudo usermod -aG docker $USER
    newgrp docker
    ```

5.  **Verify:**
    Run `docker run hello-world`. You should see "Hello from Docker!".

---

## Step 4: Project Setup (The Correct Way)
**CRITICAL:** Do NOT create the project in `/mnt/c/`. It must be in the Linux file system.

1.  **Open VS Code** on Windows.
2.  Install extensions: **WSL** and **Dev Containers**.
3.  **Connect to Linux:**
    * Click the green `><` icon (bottom-left) -> "Connect to WSL using Distro..." -> Select Ubuntu-24.04.
4.  **Create Folder (Inside VS Code Terminal):**
    ```bash
    cd ~  # Goes to /home/youruser/ (Correct)
    mkdir ai-test-architect
    cd ai-test-architect
    code .
    ```

---

## Step 5: Configuration Files

Create these files in your project root using VS Code.

### 5.1 `.devcontainer/devcontainer.json`
**Note:** We use the default workspace mapping (automatic) to ensure files are visible on your host.

```json
{
	"name": "AI Test Architect",
	"build": {
		"dockerfile": "../Dockerfile",
		"context": ".."
	},
	"customizations": {
		"vscode": {
			"extensions": [
				"ms-python.python",
				"robocorp.robotframework-lsp"
			]
		}
	},
	"forwardPorts": [8501, 8502, 8503], 
	"postCreateCommand": "pip install -r requirements.txt",
	"remoteUser": "root"
}
```

### 5.2 `.streamlit/config.toml`
Create this file to prevent the app from hanging on the "Email" prompt.

```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501

[browser]
gatherUsageStats = false
```

### 5.3 `.env`
```ini
OPENAI_API_KEY=sk-proj-.........................
```

---

## Step 6: Launch & Run

1.  **Build Container:** Press `F1` -> **"Dev Containers: Reopen in Container"**. Wait for the build.
2.  **Start App:** See `README.md` for usage instructions.

---

## Appendix: Vi Cheat Sheet
If you are forced to use `vi` in the terminal:
* **Edit:** Press `i` (Insert Mode).
* **Exit Edit:** Press `Esc`.
* **Save & Quit:** Press `Esc`, then type `:wq` and `Enter`.
* **Quit (No Save):** Press `Esc`, then type `:q!` and `Enter`.