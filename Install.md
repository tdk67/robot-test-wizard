# Installation Guide: AI Test Architect (Pure WSL Method)

This guide sets up a professional Linux development environment on Windows.

## Step 1: WSL 2 Setup
1.  Open **PowerShell** as Administrator.
2.  Run: `wsl --install -d Ubuntu-24.04` (or `wsl --update` if installed).
3.  Create username/password when prompted.

## Step 2: Enable Systemd
1.  In Ubuntu terminal: `sudo vi /etc/wsl.conf`
2.  Add:
    ```ini
    [boot]
    systemd=true
    ```
3.  Restart WSL (`wsl --shutdown` in PowerShell).

## Step 3: Install Docker Engine (Native)
Run in Ubuntu Terminal:
1.  **Repo Setup:**
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
2.  **Install:**
    ```bash
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```
3.  **Permissions:**
    ```bash
    sudo usermod -aG docker $USER
    newgrp docker
    ```

## Step 4: VS Code Integration
1.  Install **VS Code** on Windows + **WSL** Extension + **Dev Containers** Extension.
2.  **Create Project:**
    ```bash
    cd ~
    mkdir ai-test-architect
    cd ai-test-architect
    code .
    ```
3.  **First Run Note:**
    * You will see output saying **"Installing VS Code Server for Linux..."**.
    * This downloads the helper binaries to your Linux VM.
    * Wait for **"Compatibility check successful"**. VS Code will then launch automatically.

## Step 5: Container Startup
1.  Create the project files (Dockerfile, app.py, etc.).
2.  VS Code will detect the `.devcontainer` folder.
3.  Click **"Reopen in Container"** when prompted.