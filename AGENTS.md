# Agent Directives & Architecture Commandments

## 1. Zero Absolute Paths (The Iron Commandment)
* **NEVER** write absolute paths (e.g. `C:\...`, `c:/...`, `/home/...`, `/Users/...`) in any document, README, source code, test script, CLI command snippet, or config file.
* **ALWAYS** use relative paths from the repository root (e.g. `resources/config/...`, `.\run.ps1`, `cd <dir>`) or dynamically resolve paths (`Path.cwd()`, `${CURDIR}`, `${OUTPUT_DIR}`).

## 2. Secrets vs. Configuration Separation
* `.env` is strictly for private secrets and credentials (`BSTACK_PASSWORD=...`). It is git-ignored.
* Provide `.env.example` with only empty keys.
* Never put configuration parameters (model names, URLs, timeouts) in `.env`.

## 3. LEGO Architecture (Code vs. Data vs. Environment)
* `.robot` files are pure orchestration workflows with zero hardcoded test data or default variables.
* All test scenarios belong in `resources/config/testdata/*.yaml`.
* All infrastructure settings belong in `resources/config/environments/<env>/env.yaml`.
* User personas and credentials pointers belong in `resources/config/environments/<env>/users.yaml`.
