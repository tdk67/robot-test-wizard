---
name: zero-absolute-paths
description: Unconditional rule prohibiting absolute paths in any documentation, code, scripts, configurations, or command examples.
---

# The Iron Commandment: Zero Absolute Paths

## Principle: Absolute paths destroy portability, leak developer machine details, and break multi-environment workflows.

1. **NEVER put absolute paths in ANY document or code file**:
   - **Documentation**: `README.md`, guides, inline code blocks, command snippets. Never write `cd C:\...`, `c:/...`, `/home/...`, or `/Users/...`.
   - **Source Code**: Python, Robot Framework, Shell, PowerShell, Batch files. Never hardcode drive letters or machine-specific directories.
   - **Configuration & Test Data**: YAML, JSON, `.env.example`, XML. All paths must be relative to the repository root or resolved dynamically at runtime.
   - **CLI Examples**: Always use relative paths (e.g., `cd RobotFramework`, `.\run.ps1`, `python -m robot ...`).

2. **ALWAYS use relative paths or dynamic resolution**:
   - In Robot Framework: Use `${CURDIR}`, `${OUTPUT_DIR}`, or relative paths from workspace root (`resources/config/...`).
   - In Python: Use `Path.cwd()`, `Path(__file__).resolve().parent`, or relative paths.
   - In PowerShell / Bash: Use relative paths (`.\run.ps1`, `./run.sh`).
