# Execution Environment Architecture

## 1. The "Pure Linux" Philosophy
We run this project on **Windows**, but we do not use "Windows" tools.
Instead, we use **WSL 2 (Windows Subsystem for Linux)** to create a real Ubuntu kernel inside Windows.

### Why?
* **Performance:** File operations in WSL 2 are 10x faster than Windows mounts.
* **Compatibility:** Robot Framework and AI libraries behave natively (no path separator `\` vs `/` issues).
* **Docker:** We use the **Native Docker Engine** inside Linux, avoiding the performance overhead and licensing costs of "Docker Desktop."

## 2. The Stack

### Layer 1: The Host (Windows)
* **Role:** The visual interface (UI).
* **Tools:** VS Code, Web Browser (Chrome/Edge).
* **Connection:** VS Code connects remotely to the Linux layer using the "Remote - WSL" extension.

### Layer 2: The OS (WSL 2 / Ubuntu 24.04)
* **Role:** The kernel and file system.
* **Tools:** Git, Bash, Docker Daemon (`systemd`).
* **Location:** All code lives here (`\\wsl.localhost\Ubuntu\home\user\...`).

### Layer 3: The Container (Docker)
* **Role:** The isolated runtime.
* **Tools:** Python 3.12, Robot Framework 7.0, Java (for Jenkins/Allure).
* **Definition:** Defined in `.devcontainer/Dockerfile` and `devcontainer.json`.
* **Benefit:** "It works on my machine" = "It works on your machine."

## 3. The Development Container (Dev Container)
We use the VS Code **Dev Containers** specification.
When you open the project, VS Code:
1.  Reads `.devcontainer/devcontainer.json`.
2.  Builds the Docker Image defined in `Dockerfile`.
3.  Installs VS Code extensions *inside* the container (Python, RobotCode).
4.  Mounts the source code from Layer 2 into Layer 3.

**Result:** You type in VS Code on Windows, but the code executes inside a Linux Container.