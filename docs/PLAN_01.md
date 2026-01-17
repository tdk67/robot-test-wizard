# PLAN_01.md: Data-Driven Architecture & Project Structure (Hardened)

## 1. Objective
Transition to a **Metadata-Driven Architecture** that decouples logic, data, and API definitions. The system uses a **Context Builder**, **Input Contracts**, and **Granular Component Versioning** to handle complex, mixed-version environments (e.g., Customer v2.12 + Balance v3.7).

## 2. Directory Structure Specification

```text
/workspaces/ai-test-architect/
├── resources/
│   ├── config/
│   │   ├── sut/                     # ENVIRONMENT CONFIG
│   │   │   ├── UAT.yaml             # Defines Component Versions
│   │   │   └── PROD.yaml
│   │   │
│   │   └── testdata/                # INPUT VALUES
│   │       ├── UAT/
│   │       │   └── functional/
│   │       │       └── customer_flow/
│   │       │           └── create_customer.yaml
│   │
│   ├── registry/                    # API DEFINITIONS (By Component)
│   │   └── TelecomApp/              # Generic Product Name
│   │       ├── Customer/
│   │       │   └── v2.12.yaml       # Specific version logic
│   │       ├── Subscription/
│   │       │   └── v2.21.yaml
│   │       └── Balance/
│   │           └── v3.7.yaml
│   │
│   ├── templates/                   # LOGIC-LESS TEMPLATES
│   │   ├── fragments/               # Reusable Atomic Parts (Address, PO)
│   │   └── TelecomApp/
│   │       └── Customer/
│   │           └── create_customer.j2
│   │
├── testcases/
│   └── ...
```

## 3. The "Rosetta Stone" Strategy (Registry)

### 3.1 Environment Config (`config/sut/UAT.yaml`)
Instead of one "Version" flag, we map components to versions.
```yaml
BaseURL: "[https://api.uat.telco.com](https://api.uat.telco.com)"
Components:
  Customer: "v2.12"
  Subscription: "v2.21"
  Balance: "v3.7"
```

### 3.2 The Registry File (`registry/TelecomApp/Customer/v2.12.yaml`)
We solve the "Repetition" and "Monolith" issues here.

```yaml
# 1. GLOBAL DEFAULTS (Solves the "Header Copy-Paste" issue)
defaults:
  headers:
    Content-Type: "application/json"
    Authorization: "Bearer {token}"
  
# 2. COMPONENT FRAGMENTS (The "TemplateList" replacement)
components:
  Standard_Contact: "fragments/contact_medium.j2"

# 3. COMMANDS
commands:
  Create_Customer:
    path: "/customerManagement/v1/customer"  # Generic Path
    method: "POST"
    
    # INPUT CONTRACT (Validation)
    inputs:
      required: [customer_name, contact_email]
    
    # STRUCTURE (The "Builder" Logic)
    template: "TelecomApp/Customer/create_customer.j2"
    structure:
      # Optional Header Override (Only used if defined)
      # header: "special_auth_header" 
      
      contact_section:
        key: "contactMedium"
        type: "list"
        source: "contacts_input"
        item_template: "Standard_Contact" # References 'components' above
```

## 4. The Execution Flow (The "Builder" Pattern)

1.  **Launch:** `robot --variable ENV:UAT test.robot`
2.  **Loader:**
    * Reads `UAT.yaml`.
    * See `Customer: v2.12`.
    * Loads `registry/TelecomApp/Customer/v2.12.yaml`.
3.  **Command:** `Execute Command    Customer.Create_Customer`
4.  **Builder:**
    * Validates Inputs (`customer_name` present?).
    * Applies Default Headers (unless overridden).
    * Processes `structure` (Iterates `contacts_input` list, renders `contact_medium.j2`).
    * Renders Master Template with the fragments.
5.  **Result:** A pristine, complex JSON payload sent to the API.

## 5. Next Steps
* [ ] **Refactor:** Create the `registry/TelecomApp/...` folder structure.
* [ ] **Prototype:** Create `UAT.yaml` with the multi-component version map.
* [ ] **Code:** Implement the Python `RegistryLoader` that respects `env.yaml` versions.