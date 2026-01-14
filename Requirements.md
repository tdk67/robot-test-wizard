# Software Requirements Specification (SRS)
**Project:** Autonomous AI Test Architect (Telecom Billing)
**Status:** DRAFT v0.1
**Role:** Senior AI Architect & User

---

## 1. Executive Summary
The goal is to build an autonomous, "Human-in-the-Loop" test automation platform for complex Telecom Billing Systems. Unlike standard generators that produce brittle code, this system uses a **Configuration-Driven ("LEGO") Architecture**. It strictly separates logic (Robot Framework) from data (YAML), enabling the system to handle multiple application versions, customer-specific features, and air-gapped environments with high maintainability.

## 2. Core Philosophy
1.  **"LEGO" Modularity:** Code is generic; behavior is defined by stacking YAML configuration blocks (SQL rules, XPath templates, Input Data).
2.  **Diagnostics First:** The AI's primary value is not just running tests, but grouping failures to identify the *one* root cause among 100 errors.
3.  **Bi-Directional Fluidity:** Testers must be able to move seamlessly between Automated Execution (Robot) and Manual Debugging (Postman).
4.  **Empirical Verification:** We do not trust documentation blindly. We "Crash Test" existing suites against new versions to discover changes.

---

## 3. System Architecture

### 3.1 The "LEGO" Data Structure
To avoid spaghetti code, we utilize a hierarchical configuration injection system.

* **Layer 1: Logic (Robot Framework)**
    * Files: `.robot`
    * Content: Generic Keywords only (e.g., `Execute Billing Cycle`).
    * *Rule:* No hardcoded values. No version-specific logic chains (handled via dynamic imports).
* **Layer 2: The Strategy (YAML)**
    * Files: `flow_definitions.yaml`
    * Content: Defines the "Dependency Map" (e.g., `Step2.Input` comes from `Step1.Output.ID`).
* **Layer 3: The Validation Registry (YAML)**
    * Files: `validations/db.yaml`, `validations/ui.yaml`
    * Content: Reusable rules with placeholders.
    * *Example:* `CheckInvoiceStatus: { sql: "SELECT status FROM inv WHERE id={id}", expect: "PAID" }`
* **Layer 4: Configuration Overlay (YAML)**
    * **Base:** `common.yaml`
    * **Version:** `v2.0_delta.yaml` (Overrides Base)
    * **Customer:** `cust_A_feature_flags.yaml`
    * **Environment:** `prod_secrets.yaml` (Credentials)

### 3.2 The Multi-Agent System (MAS)
* **The Architect:** Analyzes Postman/Docs -> Designs the "LEGO" blocks.
* **The Librarian:** Manages the Long-Term Memory (Vector DB) to prevent duplicate keywords.
* **The Diagnostician:** Parses `output.xml`, groups failures, and reports root causes.
* **The Replayer:** Generates debug artifacts (Postman) from failed runs.

---

## 4. Key Functional Requirements

### 4.1 Ingestion & Generation
* **[REQ-GEN-01] Postman Parsing:** System must ingest Postman Collections and extract request structures.
* **[REQ-GEN-02] Variable Mapping:** System must detect variables (`{{var}}`) and ask the Human to classify them as "Config" (Environment) or "Input" (Test Data).
* **[REQ-GEN-03] PDF RAG:** System must ingest Product Documentation (PDF) to validate business logic (e.g., "Billing Cycle is 30 days").

### 4.2 Execution & Versioning
* **[REQ-EXE-01] Dockerized Runtime:** Execution must happen in a container with support for AWS Auth/VPN tunneling.
* **[REQ-EXE-02] Delta Configuration:** System must support testing multiple versions (v1, v2) simultaneously by loading the correct "Delta YAML" at runtime.
* **[REQ-EXE-03] Validation:** System must support SQL (DB), XPath (XML), and Selector (UI) validations driven by the YAML registry.

### 4.3 Diagnostics & Healing
* **[REQ-DIA-01] Root Cause Grouping:** AI must aggregate similar error logs (clustering) to reduce noise.
* **[REQ-DIA-02] Classification:** AI must distinguish between "Script Errors" (Fix automatically) and "App/Logic Errors" (Ask Human).

### 4.4 The "Replay" System (Bi-Directional)
* **[REQ-REP-01] Trace Capture:** A custom Robot Listener must record the *actual* data values used during execution.
* **[REQ-REP-02] Postman Generation:** System must generate a `debug_replay.json` (Postman Collection) from a failed run.
* **[REQ-REP-03] Data Chaining:** The generated Postman file must include JS scripts to pass variables (IDs) between requests, mimicking the automated flow.
* **[REQ-REP-04] Gap Handling:** Non-HTTP steps (DB checks) must be inserted as "Manual Instruction" requests in the Postman collection.

---

## 5. Gap Analysis (The "Unknowns")

| ID | Gap Description | Impact |
| :--- | :--- | :--- |
| **G-01** | **Postman Script Complexity:** We don't know if we can robustly translate complex Robot logic (loops, if/else) back into Postman JavaScript for the "Replay" feature. | High (Feature risk) |
| **G-02** | **Version Diffing:** We haven't defined *how* the AI detects a "Breaking Change" between v1 and v2 automatically. Is it by comparing Swagger specs? Or just running tests? | Medium (Workflow risk) |
| **G-03** | **AWS Auth in Docker:** The specifics of "logging into AWS project first" inside a container without a GUI are technically tricky (MFA, SSO tokens). | High (Blocker) |
| **G-04** | **Data State:** If a test deletes data, the "Replay" artifact might fail because the data is gone. We lack a "Data Restoration" strategy. | Medium |

---

## 6. Project TODO List (Prioritized)

### Phase 1: The Vertical Slice (Prototype)
- [ ] **Setup:** Create `Dockerfile` with Robot Framework, Python, and Postman (Newman) support.
- [ ] **Stub:** Build a simple Python FastAPI mock (Simulating Telecom Billing v1 and v2).
- [ ] **Core:** Write the Python `YamlDataDriver` to prove we can merge Base+Version configs.
- [ ] **Test:** Create ONE "Golden Path" test (Login -> Create User) in the LEGO style.

### Phase 2: The Diagnostics
- [ ] **Tool:** Write the Python script to parse `output.xml` and extract error messages.
- [ ] **AI:** Connect the parser to an LLM to test "Error Grouping" capabilities.

### Phase 3: The Replay Capability
- [ ] **Listener:** Build the Robot Framework Listener to capture execution traces.
- [ ] **Generator:** Build the logic to convert Trace -> Postman Collection JSON.