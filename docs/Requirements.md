# Software Requirements Specification (SRS)
**Project Name:** AI-Driven Autonomous Test Architect (Telecom Billing)
**Document Version:** 1.0 (Comprehensive Draft)
**Date:** January 13, 2026
**Status:** Approved for Prototyping Phase

---

## 1. Introduction

### 1.1 Purpose
The purpose of this system is to automate the creation, execution, and maintenance of regression tests for complex, evolving Telecom Billing Systems. It aims to solve the "Maintenance Nightmare" where minor application changes cause cascading test failures and code duplication.

### 1.2 Core Problem Statement
* **Brittle Automation:** Standard AI code generators produce linear scripts that are hard to update.
* **Versioning Hell:** Managing tests for multiple customer versions (v1, v2, Custom_A) leads to code duplication.
* **The "Black Box" API:** Async backend processes and undocumented behaviors make standard automation flaky.
* **Debug Gap:** Testers struggle to reproduce automated failures in their manual tools (Postman).

### 1.3 Scope
* **Target:** REST APIs, SQL Databases, Web UI (Selenium/Playwright), XML/JSON payloads.
* **Environment:** Dockerized, air-gapped (AWS/VPN tunneling required), Human-in-the-Loop.
* **Users:** Automation Engineers, Manual Testers, and Business Analysts.

---

## 2. Architectural Philosophy: The "LEGO" System

The system relies on a **Metadata-Driven Architecture**. We do not generate "Scripts"; we generate "Configurations" that drive a generic engine.

### 2.1 The Abstraction Layers
1.  **Layer 1: The Engine (Robot Framework)**
    * Contains **Generic Keywords** only (e.g., `Execute Billing Run`, `Verify Customer State`).
    * **Strategy Pattern:** Logic variations (v1 vs v2) are handled via dynamic resource imports, not `IF/ELSE` chains.
    * *Strict Rule:* No hardcoded data (IDs, Names, Counts) in `.robot` files.

2.  **Layer 2: The Data (Hierarchical YAML)**
    * **Inheritance Model:** `Runtime_Config = Base_Config + Version_Delta + Customer_Feature + Env_Secrets`.
    * **Test Input:** Defines *what* happens (Values).
    * **Dependency Map:** Explicitly defines data flow (e.g., `Order.customerId` <-- `CreateUser.response.id`).

3.  **Layer 3: The Validation Registry**
    * Validations are stored centrally and referenced by **Name**.
    * `validations/db.yaml`: Stores SQL Templates with placeholders.
    * `validations/ui.yaml`: Stores Page Objects/Selectors.
    * `validations/json.yaml`: Stores JSONPath expressions.

---

## 3. The Multi-Agent System (MAS) Roles

1.  **The Architect (Manager):**
    * Analyzes incoming requests (Postman/PDF).
    * Designs the Test Plan.
    * Asks the Human: "Is this a new pattern or should I reuse `Create_User_v1`?"

2.  **The Librarian (Memory):**
    * Maintains the **Vector Database** of existing keywords and patterns.
    * Prevents duplication by flagging "Similar Keyword Exists."

3.  **The Builder (Coder):**
    * Generates the YAML files and minimal Robot code.
    * Uses a "Symbol Table" to ensure all validation references exist.

4.  **The Diagnostician (QA):**
    * Parses `output.xml`.
    * Groups failures by **Root Cause** (Clustering).
    * Distinguishes "Script Errors" (Fixable) vs. "App Errors" (Human Review).

---

## 4. Functional Requirements

### 4.1 Ingestion & Analysis (Human-in-the-Loop)
* **[REQ-ING-01] Postman Parsing:** System must ingest Postman Collections (v2.1) including Pre-request Scripts and Environment Variables.
* **[REQ-ING-02] Documentation RAG:** System must ingest PDF documentation (e.g., Billing Logic) to validate business rules.
* **[REQ-ING-03] Interactive Mapping:** Before generating code, the Agent must present a "Mapping Proposal" to the human:
    * *Example:* "I detected `user_type: 'ADMIN'`. Is this a **Test Input** or a **Global Config**?"
* **[REQ-ING-04] Input Templating:** For large payloads (Telecom Orders), the system must store a `template.json` and only track *overrides* in the YAML.

### 4.2 Automated Execution
* **[REQ-EXE-01] Dynamic Versioning:** The system must load the correct logic implementation (`resources/v1/` vs `resources/v2/`) based on the `env.yaml` version flag.
* **[REQ-EXE-02] Feature Flags:** Tests must automatically `SKIP` if they depend on a Customer Feature not enabled in the current `env.yaml`.
* **[REQ-EXE-03] Data Cleanup:**
    * **Transactional:** Support specific Teardown blocks.
    * **Periodic:** Support a "Nuke/Reset DB" capability for nightly runs.

### 4.3 Validation Logic
* **[REQ-VAL-01] DB Verification:** Execute SQL from `validations/db.yaml`, inject variables into placeholders, and assert results.
* **[REQ-VAL-02] JSON "Targeted" Check:** Use JSONPath to validate specific fields, ignoring dynamic noise (timestamps).
* **[REQ-VAL-03] Async Polling:**
    * System must reject `Sleep`.
    * System must use `Wait Until Keyword Succeeds` using a configurable `POLL_INTERVAL`.
* **[REQ-VAL-04] UI/XML:** Verify XML via XPath and UI via Selenium selectors, both stored in the Registry.

### 4.4 Diagnostics & "Crash Test" Strategy
* **[REQ-DIA-01] Empirical Versioning:** To upgrade, the system runs the *Old Suite* against the *New App*, categorizes the failures, and asks the Human for the "Fix Pattern."
* **[REQ-DIA-02] Async Detection ("Stress Test"):** New tests are run 3x at "Machine Speed" (zero delay) to detect race conditions. If flaky, the AI suggests adding Polling.
* **[REQ-DIA-03] Root Cause Summary:** The output is not a log file, but a summary: *"3 Errors Found: 1. Auth (50 tests), 2. DB Timeout (2 tests), 3. Logic (1 test)."*

### 4.5 Bi-Directional Sync ("The Replay")
* **[REQ-REP-01] Trace Capture:** A custom Listener records the **Execution Trace** (Inputs, Outputs, Variable assignments).
* **[REQ-REP-02] Postman Generation:** From the Trace, generate a `debug.postman_collection.json`.
* **[REQ-REP-03] Chain Preservation:** Inject JavaScript (`pm.environment.set`) to pass IDs between steps, matching the Robot logic.
* **[REQ-REP-04] Gap Handling:** Insert "Manual Instruction" requests for DB/UI steps that Postman cannot perform.

---

## 5. Non-Functional Requirements (NFRs)
* **[NFR-01] Zero Duplication:** Adding a data variation must require NO changes to `.robot` files.
* **[NFR-02] Air-Gapped Operation:** Must run without public internet (Proxy/VPN support).
* **[NFR-03] Traceability:** Tests should link to Requirement IDs (if provided).
* **[NFR-04] Readability:** Robot files must be readable by Business Analysts (High-level keywords).

---

## 6. Gap Analysis (Risks & Unknowns)

| ID | Gap Description | Severity | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **G-01** | **The Stub Paradox:** Writing tests against a Stub might create a "Self-Fulfilling Prophecy" where both Stub and Test are wrong. | High | Use "Crash Test" against the real generic environment early. |
| **G-02** | **Implicit Latency:** Humans are slow; Robots are fast. Postman works, Automation fails. | High | The "Stress Test" Requirement [REQ-DIA-02]. |
| **G-03** | **AWS Auth in Docker:** Logging into AWS SSO inside a headless container is complex. | Blocker | Assume Host Networking or Service User credentials. |
| **G-04** | **Complex Postman Scripting:** We cannot easily translate complex JS logic (loops/crypto) from Postman to Robot. | Medium | Flag complex scripts for Manual Review during Ingestion. |
| **G-05** | **Deferred Consistency:** Some backend jobs run on 5-min crons and have no API status. | High | Need Admin/DB access to check job tables. |

---

## 7. Implementation Roadmap & Todo List

### Phase 1: The Prototype (Vertical Slice)
- [ ] **Todo:** Create Docker environment (Robot + Python).
- [ ] **Todo:** Build "Mock Telecom App" (v1: Simple, v2: Breaking Change).
- [ ] **Todo:** Implement `YamlDataDriver` (The Core "LEGO" Plugin).
- [ ] **Todo:** Prove "Replay" concept (Robot Trace -> Simple Postman JSON).

### Phase 2: The Agent Brain
- [ ] **Todo:** Build the "Linter" to reject Hardcoded Values.
- [ ] **Todo:** Build the "Log Parser" for Root Cause Analysis.

### Phase 3: The Advanced Workflow
- [ ] **Todo:** Implement the "Stress Test" (Async Detector).
- [ ] **Todo:** Build the Postman Ingestion (Analysis) Agent.

---

## 8. Requirements for the Prototype (Next Step)
To prove this architecture works, the **Vertical Slice** must demonstrate:
1.  **Separation:** Running the *same* Robot file with two different YAML inputs.
2.  **Versioning:** Running the test against Mock v1 (Success) and Mock v2 (Fail), then applying a "Delta Config" to fix v2 without touching v1.
3.  **Replay:** Generating a Postman file from the failed v2 run.