# Robot Framework LEGO Architecture 🧱

A modern, cloud-ready, data-driven test automation framework built on **Robot Framework 7.x**, **Playwright (Browser Library)**, and the **LEGO Architecture**.

Runs natively on Windows without requiring Docker containers or heavy background daemons.

> **💡 Context & Purpose of the `bstackdemo` Suite**:
> The `bstackdemo` e-commerce test case in this repository was implemented strictly as a **pilot Proof-of-Concept (PoC)** against a public dummy web application. Its purpose was to validate and stress-test the architectural foundations:
> 1. Proving the **LEGO pattern** (100% separation of code, YAML test data, environment configs, and masked secrets).
> 2. Evaluating the **Playwright-backed Browser Library** as a modern, high-speed replacement for legacy Selenium WebDriver.
> 3. Demonstrating structured document verification (extracting binary PDF receipts into semantic XML for XPath assertions).
> 4. Grounding AI coding assistants (like Antigravity) with local dynamic skills (`libgen`) and closed-loop `--dryrun` sandbox validation.

---

## 🎯 Core Concepts

The **LEGO Architecture** strictly decouples test execution logic, test scenario data, environment parameters, and secrets into modular, interchangeable blocks:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        testcases/*.robot                               │
│              (Pure Workflow Blueprint / Orchestration)                 │
└──────────────────────────────────▲─────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │  DataLoader Pre-Run Hook    │
                    │      (SuiteVisitor AST)     │
                    └──────┬───────────────┬──────┘
                           │               │
        ┌──────────────────▼──┐         ┌──▼─────────────────────────────┐
        │   testdata/*.yaml   │         │ environments/<env>/            │
        │ (Scenario Variables)│         │ ├── env.yaml   (URLs, Browser) │
        └─────────────────────┘         │ └── users.yaml (Personas/Env)  │
                                        └────────────────▲───────────────┘
                                                         │
                                        ┌────────────────┴───────────────┐
                                        │ .env (Git-Ignored Secrets)     │
                                        │ (BSTACK_PASSWORD, Vaults)      │
                                        └────────────────────────────────┘
```

### 1. Code vs. Data vs. Configuration Separation
* **Code (`testcases/*.robot`)**: Pure orchestration workflows. Contains zero hardcoded URLs, zero default variable values in `*** Variables ***`, and zero test data.
* **Test Data (`resources/config/testdata/*.yaml`)**: Defines test scenarios, line items, quantities, and expected totals. Adding a new test scenario requires **only editing YAML**—no code changes.
* **Environment Config (`resources/config/environments/<env>/env.yaml`)**: Stores environment-specific parameters (`BaseURL`, `Browser`, `Headless`, `Timeout`). Easily switch between `default`, `staging`, and `production`.
* **User Personas (`resources/config/environments/<env>/users.yaml`)**: Centralizes user accounts, addresses, and credential pointers for each environment. Eliminates copying address blocks across test scenarios.

### 2. Zero-Cleartext Secrets (`robot.api.types.Secret`)
* Passwords and credentials never live in Git or YAML files.
* `users.yaml` stores a pointer to the secret's environment variable (`secret_env: "BSTACK_PASSWORD"`).
* `DataLoader` automatically loads secrets from `.env` and encapsulates them in Robot Framework 7.4+ `robot.api.types.Secret` objects.
* Execution reports (`output.xml`, `log.html`) log credentials strictly as `<secret>`.

### 3. Structured PDF-to-XML Verification via XPath
* Receipts downloaded during checkout are parsed from binary PDF streams into semantic XML using `pypdf`.
* The keyword `Verify Receipt Items And Total` asserts all selected products, line item prices, and calculated grand totals using Robot Framework's standard built-in `XML` library and **XPath**.

### 4. Disk-Safe Failure Screenshots (No Accumulation)
* Failure screenshots are captured automatically when an error occurs via `Test Teardown`.
* Screenshots use deterministic filenames based on the test name:
  `${OUTPUT_DIR}/failure_${TEST_NAME}.png`
* **Zero Disk Bloat**: Re-running tests overwrites existing failure screenshots for that test instead of accumulating unbounded indexed files (`fail-screenshot-1.png`, `fail-screenshot-2.png`, etc.). When a test passes, any stale failure screenshot from prior failed runs is automatically removed.

### 5. Fast Failure & Graceful Negative Test Handling
* `Add Product To Cart` immediately verifies catalog existence using `Browser.Get Element Count`. If a product does not exist, it fails fast in 0 seconds with a clean business error instead of waiting for a 15-second timeout.
* The keyword `Add Products To Cart Or Assert Error` encapsulates negative test validation via `TRY ... EXCEPT`: if an `expected_error` is defined in the YAML scenario, it validates the error message and gracefully concludes the test with `Pass Execution`, keeping the `.robot` test case linear and uncluttered.

---

## 🎭 Modern Web Automation: Browser Library (Playwright) vs. Selenium WebDriver

A critical goal of this Proof-of-Concept was to evaluate **`robotframework-browser`** (powered by Microsoft Playwright) against the industry's traditional standard, **`robotframework-seleniumlibrary`** (Selenium WebDriver). 

### Architectural Comparison

| Dimension | `robotframework-browser` (Playwright) | `robotframework-seleniumlibrary` (Selenium) |
| :--- | :--- | :--- |
| **Connection Protocol** | Direct in-process WebSocket connection via DevTools Protocol (CDP) / Node.js. Zero intermediate proxies. | Out-of-process HTTP JSON Wire / W3C WebDriver REST protocol sending individual HTTP requests per command. |
| **Driver Management** | **Zero "Driver Hell"**: `rfbrowser init` downloads self-contained browser binaries (Chromium, Firefox, WebKit). No version mismatches. | Requires manually downloading and matching `chromedriver.exe`, `geckodriver.exe`, or relying on external managers prone to breaking when Chrome auto-updates. |
| **Execution Speed** | **Significantly Faster**: Event-driven asynchronous architecture eliminates HTTP round-trip latency. | Noticeably slower due to sequential HTTP request/response hops per locator lookup and action. |
| **Wait Mechanism** | **Native Auto-Waiting**: Automatically waits for elements to be attached, visible, stable, enabled, and editable before executing clicks or fills. | Brittle manual wait strategies (`Sleep`, `Wait Until Element Is Visible`); frequent `StaleElementReferenceException` errors. |
| **Session Isolation** | **Instant Contexts**: Creates isolated browser contexts in milliseconds with pristine cache/cookies without restarting the browser process. | Must restart the entire browser process to ensure a clean session, adding significant test suite overhead. |
| **Multi-Engine Coverage** | Out-of-the-box support for Chromium, Firefox, and WebKit (Safari engine) natively on Windows. | Requires external drivers; running true WebKit on Windows is difficult or unsupported. |
| **Advanced Capabilities** | Native file download intercept (`Promise To Wait For Download`), network mocking, route aborting, strict-mode locator checks. | Complex OS-level download directory hacks, limited network control without third-party proxy daemons. |

### Why Playwright Transformed Our Workflow
1. **Eliminated Flakiness**: Playwright automatically verifies actionability (e.g. checking if an element is animating, covered by an overlay, or disabled) before dispatching events. In this project, drawer transitions and button clicks executed flawlessly without a single artificial `Sleep`.
2. **Download Handling**: Capturing the order receipt PDF (`Download Order Receipt`) required only two lines of code: promising to wait for the download and clicking the button. Playwright captures the downloaded file event directly from the browser stream.
3. **Strict Mode Safety**: By default, Playwright alerts the engineer if a selector matches multiple elements unexpectedly, catching ambiguous DOM queries before they manifest as silent bugs.

---

## 📁 Project Structure

```text
RobotFramework/
├── testcases/
│   └── bstackdemo_e2e.robot           # E2E test workflow blueprint
├── resources/
│   ├── config/
│   │   ├── environments/
│   │   │   └── default/
│   │   │       ├── env.yaml           # URL, browser, headless, timeout
│   │   │       └── users.yaml         # User personas for 'default' env
│   │   └── testdata/
│   │       └── bstackdemo_e2e.yaml    # Scenarios (single, bundle, multi-qty, negative)
│   └── keywords/
│       ├── BStackDemoKeywords.resource # Reusable UI business keywords
│       └── custom-libs/
│           ├── DataLoader.py          # Pre-run modifier (SuiteVisitor) & config loader
│           └── PdfValidator.py        # PDF extraction & XML converter
├── results/                           # Generated reports, receipts, and screenshots
├── .env.example                       # Template for private secrets
├── .env                               # Git-ignored local secrets
├── requirements.txt                   # Python dependencies
├── run.ps1                            # PowerShell quick runner
└── run.bat                            # Windows Batch quick runner
```

---

## 🚀 Installation & Prerequisites

### Prerequisites
* Windows 10/11
* Python 3.12+ (64-bit)
* Node.js 18+ (required by Playwright)

### Setup Steps

1. **Clone the repository and navigate into the project directory:**
   ```powershell
   git clone <repository-url>
   cd <dir>
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Initialize Playwright browser binaries:**
   ```powershell
   rfbrowser init
   ```

5. **Configure Secrets:**
   Copy `.env.example` to `.env` and provide your secrets:
   ```powershell
   Copy-Item .env.example .env
   ```
   Edit `.env`:
   ```env
   BSTACK_PASSWORD=testingisfun99
   ```

6. **Generate Library Documentation & AI Skill References:**
   Build the library documentation and AI skill reference index directly from your installed virtual environment:
   ```powershell
   python tools/dump_libdocs.py
   ```

---

### 🔄 Upgrading Robot Framework & Refreshing Documentation

Generated library documentation (`docs/robot-libraries/`) and AI agent skills (`.agents/skills/`) are **intentionally excluded from Git** (`.gitignore`) to keep the repository lightweight, prevent noisy commit diffs, and ensure references always match your exact installed environment.

#### When a New Robot Framework or Library Version is Released:
1. **Upgrade packages in your virtual environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip install --upgrade robotframework robotframework-browser
   rfbrowser init
   ```
2. **Re-run the doc generator:**
   ```powershell
   python tools/dump_libdocs.py
   ```
3. **What `tools/dump_libdocs.py` automatically refreshes:**
   * **`docs/robot-libraries/*.md`**: Human-readable Markdown documentation for standard core libraries (`BuiltIn`, `Collections`, `String`, `OperatingSystem`, `XML`, `DateTime`, `Process`), 3rd party libraries (`Browser`, `RequestsLibrary`), and project custom libraries (`PdfValidator`, `DataLoader`).
   * **`docs/robot-libraries/KEYWORDS_QUICKREF.md`**: Consolidated quick-reference table indexed by library, keyword, argument signatures, and summary descriptions.
   * **`.agents/skills/robotframework-architect/`**: Self-contained skill definition (`SKILL.md`) and reference mirrors that AI coding assistants (like Antigravity or GitHub Copilot) read to generate syntax-accurate keywords and test suites.

---

## 💻 Running Tests

### 1. Using the PowerShell Quick Runner (Recommended)
```powershell
# Run with defaults (default environment + bstackdemo_e2e.robot):
.\run.ps1

# Fast sandbox syntax & keyword validation (no browser launched, completes in ~3s):
.\run.ps1 -DryRun

# Run with a custom environment config:
.\run.ps1 -Env staging -Suite testcases/bstackdemo_e2e.robot

# Run headed (non-headless) for visual debugging:
# Edit resources/config/environments/default/env.yaml and set Headless: false
```

### 2. Using the Windows Batch Runner
```cmd
.\run.bat
.\run.bat default.yaml testcases\bstackdemo_e2e.robot --dryrun
.\run.bat staging testcases\bstackdemo_e2e.robot
```

### 3. Using Robot Framework CLI Directly
```powershell
# Full execution:
.\.venv\Scripts\python.exe -m robot --outputdir results --prerunmodifier resources/keywords/custom-libs/DataLoader.py:default.yaml testcases/bstackdemo_e2e.robot

# Fast dry-run sandbox validation:
.\.venv\Scripts\python.exe -m robot --dryrun --outputdir results --prerunmodifier resources/keywords/custom-libs/DataLoader.py:default.yaml testcases/bstackdemo_e2e.robot
```

---

## ➕ Adding New Test Cases Without Writing Code

Because test logic and test data are separated, you can add new test scenarios simply by appending to [**`resources/config/testdata/bstackdemo_e2e.yaml`**](file:///c:/Data/work/RobotFramework/resources/config/testdata/bstackdemo_e2e.yaml):

### Example 1: Multi-Product Bundle
```yaml
    -   RunSettings:
            IterationName: "flagship_bundle"
            Documentation: "Purchase Galaxy S9 and iPhone 12 together"
        ScenarioVars:
            user_id: "fav_user"
            products:
              - name: "Galaxy S9"
                expected_price: "$699.00"
              - name: "iPhone 12"
                expected_price: "$799.00"
            expected_total: "$1498.00"
```

### Example 2: Same Product Multiple Quantities
```yaml
    -   RunSettings:
            IterationName: "multiple_units_same_phone"
            Documentation: "Purchase 2 units of Galaxy S9"
        ScenarioVars:
            user_id: "existing_orders_user"
            products:
              - name: "Galaxy S9"
                expected_price: "$699.00"
              - name: "Galaxy S9"
                expected_price: "$699.00"
            expected_total: "$1398.00"
```

### Example 3: Negative Test (Non-Existent Product)
```yaml
    -   RunSettings:
            IterationName: "invalid_product_catalog_check"
            Documentation: "Assert catalog validation fails fast when item is missing"
        ScenarioVars:
            user_id: "demouser"
            products:
              - name: "SuperPhone 9000 NonExistent"
                expected_price: "$999.00"
            expected_error: "Product 'SuperPhone 9000 NonExistent' was not found in the store catalog!"
```

---

## 🧠 AI-Driven Test Generation: Grounding LLMs with Local Skills & `libgen`

### 1. The Challenge: Why LLMs Hallucinate Robot Framework Code
Large Language Models (LLMs) have static pre-training knowledge cutoffs and were trained on vast amounts of obsolete internet code. Robot Framework has evolved substantially across recent major releases:
* **RF 5.0**: Introduced native `TRY ... EXCEPT` and `WHILE` loops.
* **RF 6.0**: Refactored keyword lookup and module namespaces.
* **RF 7.0+**: Introduced the native `VAR` syntax (replacing `${x}= Set Variable`), native `RETURN` statements (deprecating `[Return]`), strict keyword type validations, and the `robot.api.types.Secret` secure credential type. Legacy constructs like `:FOR` were completely removed.
* **Playwright Browser Library**: Frequently updates locator engines, strict mode behavior, and keyword signatures.

Without explicit local grounding, AI assistants (Antigravity, Claude, Copilot) frequently hallucinate deprecated or non-existent syntax from Robot Framework 3/4.

---

### 2. The Solution: Dynamic Reflection via `tools/dump_libdocs.py`
Instead of relying on LLM training weights, this project uses **active runtime introspection**:
1. When you run `python tools/dump_libdocs.py`, it executes Robot Framework's native `robot.libdoc` module directly inside your active `.venv`.
2. It reflects upon the exact library binaries installed on your machine (`BuiltIn`, `Collections`, `String`, `OperatingSystem`, `XML`, `Browser`, `RequestsLibrary`, plus custom project libraries `DataLoader` and `PdfValidator`).
3. It compiles these reflections into two critical assets:
   * **`docs/robot-libraries/`**: Comprehensive human-readable library documentation and `KEYWORDS_QUICKREF.md` (a quick-lookup table of every keyword signature and docstring).
   * **`.agents/skills/robotframework-architect/`**: An Antigravity AI Agent Skill containing `SKILL.md` (architectural directives, modern syntax examples, LEGO guidelines) and mirrored library reference tables.

---

### 3. How Antigravity Uses the Generated Skill
When you ask Antigravity (or an AI agent) to write, refactor, or debug Robot Framework tests:
1. **Skill Discovery**: On startup, Antigravity scans the project root for `.agents/skills/*/SKILL.md` and registers `robotframework-architect`.
2. **Context Activation**: The agent reads the frontmatter description (`Author, refactor, and execute modern Robot Framework 7.x test suites...`).
3. **On-Demand Reference Retrieval**: Before generating code, Antigravity uses `view_file` or `grep_search` to inspect `SKILL.md` and lookup keyword signatures in `references/KEYWORDS_QUICKREF.md`.
4. **Zero-Hallucination Output**: The agent generates code that strictly complies with:
   * The **LEGO Architecture** (pure workflow orchestration in `.robot`, test scenarios in `.yaml`).
   * **Modern RF 7.x Syntax** (`VAR`, `RETURN`, `TRY ... EXCEPT`).
   * **Exact Playwright Keywords** (e.g., `Browser.Get Element Count`, `Click`, `Wait For Elements State`).
   * **Iron Commandments** (Zero absolute paths, zero cleartext passwords).

### 4. Sandbox Syntax Checking via `--dryrun` (Closed-Loop Validation)
Before presenting newly generated test code or modified keywords to the user, the AI code generator performs **Closed-Loop Sandbox Validation**:
1. **Zero-Side-Effect Sandbox**: It executes Robot Framework's native `--dryrun` mode:
   ```powershell
   .\.venv\Scripts\python.exe -m robot --dryrun --outputdir results --prerunmodifier resources/keywords/custom-libs/DataLoader.py:default.yaml testcases/bstackdemo_e2e.robot
   ```
   *(or simply `.\run.ps1 -DryRun`)*.
2. **What `--dryrun` Validates**:
   * **Full Semantic & Syntax Parsing**: Verifies that all called keywords exist across imported resource files, built-ins, and custom Python libraries.
   * **Argument Matching & Type Validation**: Confirms that required argument counts and types match keyword contracts.
   * **Control Flow Correctness**: Validates `IF/ELSE`, `TRY/EXCEPT`, `FOR`, and `WHILE` loop block boundaries.
   * **LEGO Data Binding**: Confirms that `DataLoader` successfully parses YAML test data and binds variables to test scenarios.
   * **No Side Effects**: Does **not** launch browser windows, make network calls, or submit transactions. It operates as an instant (~3s) semantic compiler in a safe local sandbox.
3. **Automated Self-Healing Loop**: If `--dryrun` flags an issue (e.g., misspelled keyword or argument mismatch), the agent intercepts the exact line number and compiler message, corrects the code, and re-verifies.
4. **Guaranteed Compilable Code**: Only code that passes `--dryrun` with exit code `0` is delivered to the user or executed in full test runs.

---

### 5. How to Trace & Verify Antigravity's Skill Usage
You can verify and audit how Antigravity utilizes the generated skill in three ways:

#### A. Interactive UI Action Stream
In the Antigravity IDE action stream, observe the tool calls made by the agent before writing code. You will see:
* `view_file` calls targeting `.agents/skills/robotframework-architect/SKILL.md` (with `IsSkillFile: true`).
* Search or view calls targeting `.agents/skills/robotframework-architect/references/KEYWORDS_QUICKREF.md`.

#### B. Audit via Conversation Transcripts (PowerShell)
Antigravity stores complete, tamper-proof JSONL conversation logs for every session under the user's IDE application data directory. You can query these logs in PowerShell to trace exactly when and how the skill was consulted:

```powershell
# Search all conversation transcripts for skill activations:
Get-ChildItem -Path "$env:USERPROFILE\.gemini\antigravity-ide\brain\*\.system_generated\logs\transcript.jsonl" | `
    Select-String -Pattern "robotframework-architect" | `
    Select-Object -First 10

# Inspect the exact tool calls reading the skill definition:
Get-ChildItem -Path "$env:USERPROFILE\.gemini\antigravity-ide\brain\*\.system_generated\logs\transcript.jsonl" | `
    Select-String -Pattern '"IsSkillFile":true'
```

#### C. Code Output Inspection
Verify that generated `.robot` files strictly utilize modern RF 7.x constructs (e.g. `VAR`, native `RETURN`, `TRY ... EXCEPT`) rather than deprecated legacy keywords (`Set Variable`, `[Return]`, `:FOR`).

---

## 📊 Reports & Artifacts

After execution, all artifacts are generated under `results/`:
* `results/report.html`: High-level test execution summary.
* `results/log.html`: Detailed keyword-by-keyword execution trace.
* `results/output.xml`: Machine-readable test results (audited: 0 plaintext passwords).
* `results/receipt_*.pdf`: Actual PDF receipts downloaded during test execution.
* `results/failure_*.png`: Deterministic screenshots captured on test failure (auto-overwritten on re-runs).

---

## 📌 Roadmap & Future Architectural Extensions (TODO)

### 1. Application Versioning & Locator Strategy across Environments
* **Challenge**: Different environments (e.g. Staging vs Production) may host different build versions of the application with divergent DOM structures.
* **Approach**: Evaluated 3 architectural models (Versioned Locator Repository with Delta Inheritance, Union Fallbacks, and Strategy Pattern).
* **Reference**: Full analysis and trade-offs documented in [docs/APP_VERSIONING_STRATEGY.md](docs/APP_VERSIONING_STRATEGY.md). Status: Parked for decision.

### 2. Backend REST API Testing via LEGO Architecture
* **Goal**: Extend the framework to validate RESTful APIs using Robot Framework's `RequestsLibrary` following the identical decoupled pattern.
* **Architecture Alignment**:
  * **Test Data (`resources/config/testdata/<api_scenario>.yaml`)**: Defines HTTP request bodies, parameter variations, expected response status codes, and JSON schemas.
  * **Environment Config (`resources/config/environments/<env>/env.yaml`)**: Stores API base URLs, endpoint routes, default headers, and timeouts per target tier.
  * **Secrets (`.env`)**: Stores Bearer tokens, API keys, and client secrets with zero-cleartext masking.
* **Full E2E Integration**: Enables complete end-to-end multi-layer tests (e.g. create record via REST API -> verify UI representation in Browser -> assert downloaded PDF receipt).

### 3. Universal Database Testing via SQLAlchemy (Zero Heavy C-Libraries)
* **Goal**: Query and verify database state across enterprise engines (Oracle, PostgreSQL, MySQL, SQL Server, SQLite) without installing heavy, platform-specific C-libraries or vendor client bundles (e.g. Oracle Instant Client, ODBC drivers, cx_Oracle).
* **Pure-Python Engine via SQLAlchemy**:
  * Implement a lightweight custom library powered by **SQLAlchemy** using pure-Python drivers (such as `python-oracledb` in **Thin Mode**, which requires no Oracle Client installation whatsoever).
* **Configuration-Driven Connections**:
  * Connection strings and DSN templates configured per environment in `env.yaml` (e.g. `oracle+oracledb://{user}:{password}@{host}:{port}/?service_name={service}`).
  * DB credentials securely mapped from `.env` using `DataLoader` secrets resolution.
* **Generic Verification Keywords**:
  * Provide generic query keywords (e.g. `Execute Sql Query    SELECT status, total FROM orders WHERE id=:id`) returning structured dictionaries for seamless Robot Framework assertions across UI, API, and DB layers.