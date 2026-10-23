# Project Concept: The "Autonomous Test Architect" MCP Server
**Subtitle:** A Metadata-Driven, Self-Healing Automation Ecosystem for Complex Telecom Business Processes

## 1. Executive Summary
This project aims to build a Model Context Protocol (MCP) server that transforms a standard Large Language Model (LLM) into an **Autonomous Test Architect**. Unlike existing solutions that merely "execute scripts" or "write code snippets," this system focuses on **Stateful Orchestration** and **Lifecycle Management** of complex business processes (e.g., Telecom Billing).

It leverages a **"LEGO" Architecture**, strictly separating **Test Logic** (Code Blocks/Keywords) from **Test Data** (Data Blocks/Blueprints). The MCP server acts as the bridge, allowing the AI to "compose" valid, executable tests by snapping these proven blocks together, ensuring high reusability and zero code duplication.

---

## 2. The Unique "Blue Ocean" Niche
Most AI test tools today focus on *generating* code (writing Python/Robot scripts from scratch). This leads to "Maintenance Hell" where every test is a unique snowflake.

**Our Niche:**
We do not generate new logic for every test. We **compose** tests from a curated library of **proven, version-controlled components**.
* **Context-Aware Orchestration:** The AI understands that "Suspending a Subscription" is not just an API call; it is a *sequence* that requires a Customer, a Contract, and a specific Business State.
* **Protocol-Agnostic Validation:** The AI can seamlessly switch between validating an API response (JSON), checking a database row (SQL), and verifying a UI element (Selenium) within the same logical step.
* **Agentic Self-Healing:** When a test fails, the AI doesn't just report it. It analyzes the "Visual/DOM State," clusters similar failures, and proposes updates to the central **Metadata Registry**, fixing 50 tests with one edit.

---

## 3. The "LEGO" Architecture: Data & Logic Separation
The core philosophy is that **Code and Data must be decoupled**. The MCP server enforces this structure.

### 3.1 Code Blocks (The "Tools")
* **Definition:** Reusable Robot Framework keywords that perform a specific technical action (e.g., `Create Customer via API`, `Run Billing Job`).
* **Characteristics:**
    * **Generic:** They never contain hardcoded data (no "John Doe", no "Product ID 123").
    * **Versioned:** Different implementations (v1 vs v2) are loaded dynamically based on the Environment Config.
    * **Contract-Driven:** Each keyword has a strict "Input Contract" defining exactly what data it needs to run.

### 3.2 Data Blocks (The "Blueprints")
* **Definition:** Hierarchical YAML structures that define *what* to create.
* **Fragments (Atoms):** Small, reusable units (e.g., `Billing_Address_Germany`, `Credit_Card_Visa`).
* **Blueprints (Molecules):** Composite structures (e.g., `Postpaid_Subscription_Base`).
    * *Example:* "Postpaid Subscription" = "Voice Fragment" + "Data Fragment" + "SMS Fragment".
* **Usage:** When the AI builds a test, it selects a Blueprint and only defines the *overrides* (e.g., "Use the Postpaid Blueprint, but change the Data Plan to 50GB").

---

## 4. MCP Server Capabilities (The AI Toolset)

The MCP server exposes specific tools that allow the AI to act as different "Agents" within the system.

### Role A: The Librarian (Discovery & Reusability)
* **`search_component_registry(query)`**:
    * Allows the AI to find existing Keywords and Blueprints (e.g., "Find me a way to create a prepaid customer").
    * **Key Feature:** Returns the "Input Contract" so the AI knows strictly what arguments are required.
* **`get_blueprint_structure(blueprint_name)`**:
    * Returns the JSON/YAML schema of a data block (e.g., `Postpaid_Base`) so the AI knows where to inject new values.

### Role B: The Architect (Composition & Orchestration)
* **`chain_dependency_flow(target_goal)`**:
    * The AI asks: "I need to test 'Partial Payment'."
    * The MCP answers: "To do that, you first need a **Bill** (Status: Unpaid). To get a Bill, you need a **Contract**. To get a Contract, you need a **Customer**."
* **`suggest_data_overrides(base_blueprint, new_requirement)`**:
    * The AI inputs a natural language request ("Create a customer with a specialized tax ID").
    * The MCP compares this against the `Standard_Customer` blueprint and generates the minimal YAML "Delta" configuration.

### Role C: The Verifier (Validation & State)
* **`validate_business_state(entity_id, expected_state)`**:
    * Executes a multi-layer check:
        1.  **API:** Checks HTTP 200 OK.
        2.  **DB:** Queries the SQL database to ensure `status='ACTIVE'`.
        3.  **Logic:** Uses JSONPath to verify specific payload fields (ignoring dynamic timestamps).
* **`execute_async_job(job_name)`**:
    * Triggers backend processes (e.g., "Run Billing Cycle") and *polls* until completion, preventing "Sleep" commands in tests.

### Role D: The Diagnostician (Root Cause Analysis)
* **`cluster_failures(test_run_id)`**:
    * Parses `output.xml`. Instead of reporting 50 failures, it reports: *"Cluster A: 45 tests failed due to 'Invalid Token' (Auth Issue). Cluster B: 5 tests failed due to 'Calculation Mismatch' (Logic Issue)."*
* **`introspect_environment_state()`**:
    * Captures the "Moment of Failure": Pulls API logs, DB row state, and screenshots to help the AI distinguish between a **Broken Test** (needs update) and a **Broken Feature** (needs bug report).

---

## 5. Workflow Example: "Testing a Partial Payment"

Here is how the AI uses the MCP server to build this complex test case:

1.  **Ingest Request:** User says, "Verify that a Postpaid customer can make a partial bill payment."
2.  **Discovery (Librarian):**
    * AI calls `search_component_registry` and finds:
        * Keyword: `Billing.Make_Payment`
        * Blueprint: `Payment.Standard_Credit_Card`
3.  **Orchestration (Architect):**
    * AI realizes `Make_Payment` requires an `invoice_id`.
    * AI backtracks dependencies: "I need `Generate_Bill` -> `Create_Subscription` -> `Create_Customer`."
4.  **Assembly (Builder):**
    * AI composes the test using **Proven Blocks**:
        * *Step 1:* `Create_Customer` (using `Customer.Blueprint.Standard`).
        * *Step 2:* `Create_Subscription` (using `Subscription.Blueprint.Postpaid_Voice_Data`).
        * *Step 3:* `Generate_Bill` (triggers async job).
        * *Step 4:* `Make_Payment` (using `Payment.Blueprint.Partial` override: `amount=50.00`).
5.  **Validation (Verifier):**
    * AI adds a validation step: `Verify_Invoice_Balance` (expects `Remaining = Total - 50.00`).

---

## 6. Technical Implementation Details
* **Environment:** "Pure Linux" (WSL 2) running Native Docker Containers.
* **Core Engine:** Robot Framework 7.x (Python 3.12).
* **Data Driver:** A custom `RegistryLoader` (Python) that merges Base + Version + Environment YAMLs at runtime.
* **Security:**
    * **Air-Gapped Ready:** No dependency on public API calls for logic.
    * **Safe Execution:** The MCP server runs as a "Service User" with read-only DB access, preventing accidental data destruction (except in designated "Sandbox" environments).

## 7. Next Steps for Prototyping
1.  **Define the Registry Schema:** Create the `.yaml` structure for a "Customer" and "Subscription" blueprint.
2.  **Build the `RegistryLoader`:** The Python class that the MCP server will use to read these blueprints.
3.  **Implement the "Hello World" MCP:** A simple server that allows the AI to "List Available Blueprints."