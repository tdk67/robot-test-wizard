# Robot Framework LEGO Architecture 🧱

A modern, cloud-ready, data-driven test automation framework built on **Robot Framework 7.x**, **Playwright (Browser Library)**, and the **LEGO Architecture**.

Runs natively on Windows without requiring Docker containers or heavy background daemons.

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
* The test case queries items and totals using Robot Framework's standard built-in `XML` library and **XPath**:
  ```robot
  ${xml_text}=    Convert Pdf To Xml    ${pdf_file}
  ${xml}=         Parse Xml             ${xml_text}
  ${price}=       Get Element Text      ${xml}    xpath=items/item[type='Galaxy S9']/price
  ${total}=       Get Element Text      ${xml}    xpath=total_price
  ```

### 4. Disk-Safe Failure Screenshots (No Accumulation)
* Failure screenshots are captured automatically when an error occurs via `Test Teardown`.
* Screenshots use deterministic filenames based on the test name:
  `${OUTPUT_DIR}/failure_${TEST_NAME}.png`
* **Zero Disk Bloat**: Re-running tests overwrites existing failure screenshots for that test instead of accumulating unbounded indexed files (`fail-screenshot-1.png`, `fail-screenshot-2.png`, etc.).

### 5. Fast Failure & Negative Test Handling (`TRY / EXCEPT`)
* `Add Product To Cart` immediately verifies catalog existence using `Browser.Get Element Count`. If a product does not exist, it fails fast in 0 seconds with a clean business error instead of waiting for a 15-second timeout.
* Negative test cases in YAML (with `expected_error`) use native Robot Framework `TRY ... EXCEPT` to validate expected error conditions gracefully.

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
   cd RobotFramework
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
   Build the library documentation and AI skill reference index directly from your installed packages:
   ```powershell
   python tools/dump_libdocs.py
   ```
   > **Note**: Generated library docs (`docs/robot-libraries/`) and skill references (`.agents/skills/`) are git-ignored to keep the repository lightweight. Run `python tools/dump_libdocs.py` whenever you upgrade Robot Framework or install new libraries to refresh syntax references automatically.

---

## 💻 Running Tests

### 1. Using the PowerShell Quick Runner (Recommended)
```powershell
# Run with defaults (default environment + bstackdemo_e2e.robot):
.\run.ps1

# Run with a custom environment config:
.\run.ps1 -Env staging -Suite testcases/bstackdemo_e2e.robot

# Run headed (non-headless) for visual debugging:
# Edit resources/config/environments/default/env.yaml and set Headless: false
```

### 2. Using the Windows Batch Runner
```cmd
.\run.bat
.\run.bat staging testcases\bstackdemo_e2e.robot
```

### 3. Using Robot Framework CLI Directly
```powershell
.\.venv\Scripts\python.exe -m robot --outputdir results --prerunmodifier resources/keywords/custom-libs/DataLoader.py:default.yaml testcases/bstackdemo_e2e.robot
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

When you run `.\run.ps1`, `DataLoader` dynamically expands each YAML scenario into an independent test iteration with its own documentation, assertions, and reporting.

---

## 📊 Reports & Artifacts

After execution, all artifacts are generated under `results/`:
* `results/report.html`: High-level test execution summary.
* `results/log.html`: Detailed keyword-by-keyword execution trace.
* `results/output.xml`: Machine-readable test results (audited: 0 plaintext passwords).
* `results/receipt_*.pdf`: Actual PDF receipts downloaded during test execution.
* `results/failure_*.png`: Deterministic screenshots captured on test failure (auto-overwritten on re-runs).

---

## 📌 Roadmap & Pending Architectural Decisions (TODO)

* [ ] **Application Versioning & Locator Strategy across Environments**:
  * Different environments (e.g. Staging vs Production) may run different revisions of the application with varying DOM structures.
  * Evaluated 3 architectural models (Versioned Locator Repository with Delta Inheritance, Union Fallbacks, and Strategy Pattern).
  * Full analysis and trade-offs documented in [docs/APP_VERSIONING_STRATEGY.md](docs/APP_VERSIONING_STRATEGY.md). Status: Parked for decision.